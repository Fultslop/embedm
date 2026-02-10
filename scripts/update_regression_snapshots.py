#!/usr/bin/env python3
"""Update regression test snapshots after intentional changes.

This script processes all source files for each test suite and writes
the output to the corresponding snapshots directory.

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

# Suite definitions: (name, sources_dir, snapshots_dir, excludes)
# Keep in sync with tests/test_regression.py SUITES
SUITES = [
    ("regression", "tests/regression/sources", "tests/regression/snapshots", ["data"]),
    ("manual", "doc/manual/src", "doc/manual/src/compiled", ["compiled", "examples"]),
]


def discover_source_files(sources_dir: Path, excludes: list) -> list:
    """Discover all .md files in sources directory, skipping excluded subdirectories."""
    source_files = []
    for md_file in sources_dir.rglob("*.md"):
        if any(excluded in md_file.parts for excluded in excludes):
            continue
        source_files.append(md_file)
    return sorted(source_files)


def process_file(source_file: Path, output_file: Path) -> bool:
    """Process a single markdown file through EmbedM."""
    processor = PhaseProcessor()

    try:
        result = processor.process_all_phases(str(source_file))

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        return True
    except Exception as e:
        error_msg = f"# Processing Error\n\n> [!CAUTION]\n> **Error:** {str(e)}\n"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_msg)

        return False


def main():
    """Update snapshots for all test suites."""
    total_processed = 0
    total_errors = 0
    snapshot_paths = []

    for suite_name, sources_path, snapshots_path, excludes in SUITES:
        sources_dir = Path(sources_path)
        snapshots_dir = Path(snapshots_path)

        print(f"🔄 [{suite_name}] Processing sources from {sources_path}")

        if not sources_dir.exists():
            print(f"   ❌ Sources directory not found: {sources_dir}")
            print()
            continue

        snapshots_dir.mkdir(parents=True, exist_ok=True)
        snapshot_paths.append(snapshots_path)

        source_files = discover_source_files(sources_dir, excludes)

        if not source_files:
            print(f"   ⚠️  No source files found")
            print()
            continue

        processed_count = 0
        error_count = 0

        for source_file in source_files:
            rel_path = source_file.relative_to(sources_dir)
            output_file = snapshots_dir / rel_path
            print(f"   {rel_path}... ", end="")

            success = process_file(source_file, output_file)
            if success:
                print("✅")
                processed_count += 1
            else:
                print("❌ (error captured in snapshot)")
                error_count += 1

        total_processed += processed_count
        total_errors += error_count
        print()

    print(f"✅ Updated {total_processed} snapshots across {len(SUITES)} suites")

    if total_errors > 0:
        print(f"⚠️  {total_errors} files had processing errors (captured in snapshots)")

    print()
    print("📝 Snapshots updated. Review changes with:")
    for path in snapshot_paths:
        print(f"   git diff {path}/")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
