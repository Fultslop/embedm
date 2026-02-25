import subprocess
import sys
import argparse

def check_permissions():
    """Checks if the authenticated user has admin rights to the repo."""
    try:
        # Get the current user's permission level for this repo
        # Result looks like: {"permission": "admin"}
        perm_json = run_cmd("gh api repos/:owner/:repo/collaborators/{owner}/permission", dry_run=False)
        if '"permission":"admin"' not in perm_json.replace(" ", ""):
            print("❌ Access Denied: You must have Admin permissions to release.")
            sys.exit(1)
    except Exception:
        print("⚠️ Could not verify permissions. Ensure 'gh' is logged in.")
        sys.exit(1)

def run_cmd(cmd, dry_run=False):
    """Executes a command or just prints it if in dry-run mode."""
    if dry_run:
        print(f"[DRY-RUN] Would execute: {cmd}")
        return "v0.0.0-dryrun" # Dummy version for dry run logic
    
    try:
        # shell=True is necessary for Windows to find .exe files in PATH
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {cmd}\n{e.output}")
        sys.exit(1)

def main():
    check_permissions()

    parser = argparse.ArgumentParser(description="Release manager for embedm")
    parser.add_argument("version", nargs="?", default="patch", help="major, minor, patch, or a specific version (e.g. 1.0.0)")
    parser.add_argument("--dry-run", action="store_true", help="See what would happen without making changes")
    args = parser.parse_args()

    print(f"🚀 Starting {'DRY RUN ' if args.dry_run else ''}release process...")

    # 1. Bump version in pyproject.toml
    bump_type = args.version
    if bump_type in ["major", "minor", "patch"]:
        run_cmd(f"uv version --bump {bump_type}", args.dry_run)
    else:
        run_cmd(f"uv version {bump_type}", args.dry_run)

    # 2. Get the new version string
    new_version = run_cmd("uv version --short", args.dry_run)
    tag = f"v{new_version}"
    
    # 3. Git Operations
    print(f"📦 Committing and tagging {tag}...")
    run_cmd("git add pyproject.toml", args.dry_run)
    run_cmd(f'git commit -m "chore: bump version to {new_version}"', args.dry_run)
    run_cmd(f"git tag -a {tag} -m \"Release {tag}\"", args.dry_run)

    # 4. Push and Release
    print(f"⬆️ Pushing to GitHub...")
    run_cmd("git push origin main", args.dry_run)
    run_cmd("git push origin --tags", args.dry_run)

    print(f"✨ Creating GitHub Release...")
    run_cmd(f"gh release create {tag} --generate-notes", args.dry_run)

    print(f"\n✅ Done! {'(Dry run complete - no changes made)' if args.dry_run else 'Release pushed.'}")

if __name__ == "__main__":
    main()