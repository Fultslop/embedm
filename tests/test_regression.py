"""Regression tests for EmbedM output.

These tests process markdown files in tests/regression/sources/ and compare
the output against snapshots in tests/regression/snapshots/. This catches
regressions in output formatting, TOC generation, table conversion, etc.

Directory structure:
    tests/regression/
    ├── sources/           # Input markdown files with embeds
    │   ├── *.md
    │   ├── circular_deps/ # Subdirectory with test cases
    │   └── data/          # Supporting files (CSV, JSON, Python)
    ├── snapshots/         # Expected output (committed to git)
    │   ├── *.md
    │   └── circular_deps/
    └── actual/            # Actual output (gitignored, generated during tests)

To update snapshots after intentional changes:
    python scripts/update_regression_snapshots.py
"""

import shutil
import filecmp
from pathlib import Path
from typing import List

import pytest

from embedm.phases import PhaseProcessor


class TestRegression:
    """Regression test suite for EmbedM output."""

    @pytest.fixture(autouse=True)
    def setup_actual_dir(self):
        """Set up actual output directory before each test."""
        actual_dir = Path("tests/regression/actual")

        # Clean existing actual directory
        if actual_dir.exists():
            shutil.rmtree(actual_dir)

        # Create fresh actual directory
        actual_dir.mkdir(parents=True, exist_ok=True)

        # Ensure plugins are registered (force import and registration)
        from embedm.registry import get_default_registry
        from embedm_plugins import FilePlugin, LayoutPlugin, TOCPlugin, TablePlugin

        registry = get_default_registry()

        # Register all built-in plugins if not already registered
        for PluginClass in [FilePlugin, LayoutPlugin, TOCPlugin, TablePlugin]:
            plugin = PluginClass()
            # Check if already registered to avoid conflicts
            for embed_type in plugin.embed_types:
                for phase in plugin.phases:
                    if not registry.is_registered(embed_type, phase):
                        try:
                            registry.register(plugin)
                            break  # Only register once per plugin
                        except ValueError:
                            pass  # Already registered by another iteration

        yield

        # Note: We don't clean up after tests so users can inspect diffs

    def _process_file(self, source_file: Path, output_file: Path) -> None:
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
        except Exception as e:
            # Write error to output file
            error_msg = f"# Processing Error\n\n> [!CAUTION]\n> **Error:** {str(e)}\n"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)

    def _discover_source_files(self, sources_dir: Path) -> List[Path]:
        """Discover all .md files in sources directory (excluding data/).

        Args:
            sources_dir: Path to sources directory

        Returns:
            List of source file paths relative to sources_dir
        """
        source_files = []

        # Find all .md files recursively, excluding data/ directory
        for md_file in sources_dir.rglob("*.md"):
            # Skip files in data/ directory
            if "data" in md_file.parts:
                continue

            source_files.append(md_file)

        return sorted(source_files)

    def _get_relative_path(self, file_path: Path, base_dir: Path) -> Path:
        """Get relative path from base directory.

        Args:
            file_path: Absolute file path
            base_dir: Base directory

        Returns:
            Relative path from base_dir
        """
        try:
            return file_path.relative_to(base_dir)
        except ValueError:
            # If file_path is not relative to base_dir, return as-is
            return file_path

    def test_regression_suite(self):
        """Run regression test suite comparing output against snapshots.

        This test automatically discovers all .md files in tests/regression/sources/
        (excluding data/ directory) and:
        1. Processes each file through EmbedM
        2. Writes output to tests/regression/actual/
        3. Compares with tests/regression/snapshots/
        4. Deletes matching files from actual/
        5. Fails if there are any differences

        To add new regression tests:
        - Simply add .md files to tests/regression/sources/
        - Run: python scripts/update_regression_snapshots.py
        - Commit both sources/ and snapshots/

        If test fails, inspect tests/regression/actual/ for diffs.
        """
        sources_dir = Path("tests/regression/sources")
        snapshots_dir = Path("tests/regression/snapshots")
        actual_dir = Path("tests/regression/actual")

        # Verify directories exist
        assert sources_dir.exists(), "Sources directory not found"
        assert snapshots_dir.exists(), "Snapshots directory not found"

        # Discover all source files
        source_files = self._discover_source_files(sources_dir)

        if not source_files:
            pytest.skip("No source files found in tests/regression/sources/")

        # Process all source files
        for source_file in source_files:
            rel_path = self._get_relative_path(source_file, sources_dir)
            output_file = actual_dir / rel_path

            self._process_file(source_file, output_file)

        # Compare with snapshots and collect differences
        differences = []
        matched_files = []

        # Check all files in actual/
        for actual_file in actual_dir.rglob("*.md"):
            rel_path = self._get_relative_path(actual_file, actual_dir)
            snapshot_file = snapshots_dir / rel_path

            if not snapshot_file.exists():
                differences.append(f"New file: {rel_path}")
                continue

            # Compare content
            if filecmp.cmp(actual_file, snapshot_file, shallow=False):
                # Match! Mark for deletion
                matched_files.append(actual_file)
            else:
                # Difference! Keep file and record
                differences.append(f"Modified: {rel_path}")

        # Check for deleted files (in snapshots but not in actual)
        for snapshot_file in snapshots_dir.rglob("*.md"):
            rel_path = self._get_relative_path(snapshot_file, snapshots_dir)
            actual_file = actual_dir / rel_path

            if not actual_file.exists():
                differences.append(f"Deleted: {rel_path}")

        # Delete matching files
        for file_path in matched_files:
            file_path.unlink()

        # Clean up empty directories
        for dirpath in sorted(actual_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not list(dirpath.iterdir()):
                dirpath.rmdir()

        # Assert no differences
        if differences:
            diff_msg = "Regression test failed. Differences found:\n"
            diff_msg += "\n".join(f"  - {diff}" for diff in differences)
            diff_msg += "\n\nInspect tests/regression/actual/ for detailed diffs."
            diff_msg += "\nTo update snapshots: python scripts/update_regression_snapshots.py"
            pytest.fail(diff_msg)

        # Verify actual directory is empty (all files matched)
        remaining_files = list(actual_dir.rglob("*.md"))
        if remaining_files:
            files_list = "\n".join(f"  - {f.relative_to(actual_dir)}" for f in remaining_files)
            pytest.fail(
                f"Regression test failed. Files with differences:\n{files_list}\n\n"
                "Inspect tests/regression/actual/ for detailed diffs.\n"
                "To update snapshots: python scripts/update_regression_snapshots.py"
            )
