import subprocess
import sys
import argparse
import subprocess
import tomllib  # Built-in in Python 3.11+

def check_permissions():
    """Checks if the authenticated user has admin rights to the repo."""
    try:
        # Get the current user's permission level for this repo
        # Result looks like: {"permission": "admin"}
        perm_json = run_cmd("gh api repos/:owner/:repo/collaborators/{owner}/permission", dry_run=False)
        if '"permission":"admin"' not in perm_json.replace(" ", ""):
            print("[ERROR] Access Denied: You must have Admin permissions to release.")
            sys.exit(1)
    except Exception:
        print("[WARN] Could not verify permissions. Ensure 'gh' is logged in.")
        sys.exit(1)


def get_current_version():
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return data["project"]["version"]

def calculate_next_version(current, bump_type):
    # Simple semantic versioning logic for dry-run visualization
    major, minor, patch = map(int, current.split('.'))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else: # patch
        return f"{major}.{minor}.{patch + 1}"

def run_cmd(cmd, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Would execute: {cmd}")
        return None
    
    try:
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error executing: {cmd}\n{e.output}")
        sys.exit(1)

def main():
    check_permissions()
    parser = argparse.ArgumentParser()
    parser.add_argument("version", nargs="?", default="patch")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    current_v = get_current_version()
    
    # Calculate what the version WILL be
    if args.version in ["major", "minor", "patch"]:
        target_v = calculate_next_version(current_v, args.version)
    else:
        target_v = args.version # User provided specific version like "1.0.0"

    tag = f"v{target_v}"

    print(f"Starting {'DRY RUN ' if args.dry_run else ''}release: {current_v} -> {target_v}")

    # 1. Bump version
    run_cmd(f"uv version {target_v}", args.dry_run)

    # 2. Git Operations
    print(f"Committing and tagging {tag}...")
    run_cmd("git add pyproject.toml", args.dry_run)
    run_cmd(f'git commit -m "chore: bump version to {target_v}"', args.dry_run)
    run_cmd(f"git tag -a {tag} -m \"Release {tag}\"", args.dry_run)

    # 3. Push and Release
    print(f"Pushing to GitHub...")
    run_cmd("git push origin main", args.dry_run)
    run_cmd("git push origin --tags", args.dry_run)

    print(f"Creating GitHub Release...")
    run_cmd(f"gh release create {tag} --generate-notes", args.dry_run)

    if args.dry_run:
        print(f"\n[OK] Dry run complete. It would have created release {tag}")

if __name__ == "__main__":
    main()