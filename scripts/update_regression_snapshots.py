#!/usr/bin/env python3
"""Update regression test snapshots after intentional changes.

This script processes all source files in tests/regression/sources/ and
copies the output to tests/regression/snapshots/, replacing the existing
snapshots with the new output.

Use this when:
- You've made intentional changes to output format
- You've added new features that change output
- You've fixed bugs that change expected output

DO NOT use this to bypass failing tests - always verify changes are correct!
"""

import sys
import shutil
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from embedm.phases import PhaseProcessor


def process_file(source_file: Path, output_file: Path) -> None:
    """Process a single markdown file through EmbedM.

    Args:
        source_file: Path to source markdown file
        output_file: Path to output file
    """
    # Create processor with default limits
    processor = PhaseProcessor()

    # Process all phases
    try:
        result = processor.process_all_phases(str(source_file))

        # Write output
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        return True
    except Exception as e:
        # Write error to output file
        error_msg = f"# Processing Error\n\n> [!CAUTION]\n> **Error:** {str(e)}\n"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_msg)

        return False


def main():
    """Update all regression test snapshots."""
    sources_dir = Path("tests/regression/sources")
    snapshots_dir = Path("tests/regression/snapshots")

    if not sources_dir.exists():
        print(f"❌ Error: Sources directory not found: {sources_dir}")
        return 1

    # Create snapshots directory if it doesn't exist
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    processed_count = 0
    error_count = 0

    print("🔄 Processing regression test sources...")
    print()

    # Process files in root directory
    for source_file in sorted(sources_dir.glob("*.md")):
        output_file = snapshots_dir / source_file.name
        print(f"  Processing: {source_file.name}... ", end="")

        success = process_file(source_file, output_file)
        if success:
            print("✅")
            processed_count += 1
        else:
            print("❌ (error captured in snapshot)")
            error_count += 1

    # Process files in subdirectories (e.g., circular_deps/)
    for subdir in sorted(sources_dir.iterdir()):
        if not subdir.is_dir() or subdir.name == "data":
            continue  # Skip data directory

        print(f"\n  Processing {subdir.name}/:")

        snapshot_subdir = snapshots_dir / subdir.name
        snapshot_subdir.mkdir(parents=True, exist_ok=True)

        for source_file in sorted(subdir.glob("*.md")):
            output_file = snapshot_subdir / source_file.name
            print(f"    {source_file.name}... ", end="")

            success = process_file(source_file, output_file)
            if success:
                print("✅")
                processed_count += 1
            else:
                print("❌ (error captured in snapshot)")
                error_count += 1

    print()
    print(f"✅ Updated {processed_count} snapshots")

    if error_count > 0:
        print(f"⚠️  {error_count} files had processing errors (captured in snapshots)")

    print()
    print("📝 Snapshots updated. Review changes with:")
    print("   git diff tests/regression/snapshots/")
    print()
    print("💾 Commit updated snapshots with:")
    print("   git add tests/regression/snapshots/")
    print("   git commit -m 'Update regression test snapshots'")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
