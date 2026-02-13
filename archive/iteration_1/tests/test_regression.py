"""Regression tests for EmbedM output.

These tests process markdown files through EmbedM and compare the output
against snapshots. This catches regressions in output formatting, TOC
generation, table conversion, etc.

Test suites are defined in SUITES below. Each suite specifies:
- sources_dir: where to find input .md files
- snapshots_dir: where expected output lives
- excludes: subdirectory names to skip during discovery

To update snapshots after intentional changes:
    python scripts/update_regression_snapshots.py
"""

import shutil
import filecmp
from pathlib import Path
from typing import List

import pytest

from embedm.phases import PhaseProcessor

# Suite definitions: (name, sources_dir, snapshots_dir, excludes)
# Each suite discovers .md files in sources_dir, processes them, and
# compares against snapshots_dir. Subdirectories in excludes are skipped.
SUITES = [
    ("regression", "tests/regression/sources", "tests/regression/snapshots", ["data"]),
    ("manual", "doc/manual/src", "doc/manual/src/compiled", ["compiled", "examples"]),
    ("readme", "doc/readme/src", "doc/readme/compiled", ["compiled", "examples"]),
]


class TestRegression:
    """Regression test suite for EmbedM output."""

    @pytest.fixture(autouse=True)
    def setup_plugins(self):
        """Ensure plugins are registered before each test."""
        from embedm.registry import get_default_registry
        from embedm_plugins import FilePlugin, LayoutPlugin, TOCPlugin, TablePlugin, MermaidPlugin

        registry = get_default_registry()

        # Register all built-in plugins if not already registered
        for PluginClass in [FilePlugin, LayoutPlugin, TOCPlugin, TablePlugin, MermaidPlugin]:
            plugin = PluginClass()
            for embed_type in plugin.embed_types:
                for phase in plugin.phases:
                    if not registry.is_registered(embed_type, phase):
                        try:
                            registry.register(plugin)
                            break
                        except ValueError:
                            pass

        yield

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

    def _discover_source_files(self, sources_dir: Path, excludes: List[str]) -> List[Path]:
        """Discover all .md files in sources directory, skipping excluded subdirectories.

        Args:
            sources_dir: Path to sources directory
            excludes: List of subdirectory names to skip

        Returns:
            List of source file paths
        """
        source_files = []

        for md_file in sources_dir.rglob("*.md"):
            if any(excluded in md_file.parts for excluded in excludes):
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

    @pytest.mark.parametrize(
        "suite_name,sources_dir,snapshots_dir,excludes",
        SUITES,
        ids=[s[0] for s in SUITES],
    )
    def test_suite(self, suite_name, sources_dir, snapshots_dir, excludes):
        """Run a regression suite comparing processed output against snapshots.

        Each suite discovers .md files in its sources directory, processes them
        through EmbedM, and compares the output against its snapshots directory.

        If the test fails, inspect tests/regression/actual/<suite_name>/ for diffs.
        To update snapshots: python scripts/update_regression_snapshots.py
        """
        sources = Path(sources_dir)
        snapshots = Path(snapshots_dir)
        actual = Path(f"tests/regression/actual/{suite_name}")

        # Clean and create actual dir for this suite
        if actual.exists():
            shutil.rmtree(actual)
        actual.mkdir(parents=True, exist_ok=True)

        # Verify directories exist
        assert sources.exists(), f"Sources directory not found: {sources}"
        assert snapshots.exists(), f"Snapshots directory not found: {snapshots}"

        # Discover all source files
        source_files = self._discover_source_files(sources, excludes)

        if not source_files:
            pytest.skip(f"No source files found in {sources}")

        # Process all source files
        for source_file in source_files:
            rel_path = self._get_relative_path(source_file, sources)
            output_file = actual / rel_path
            self._process_file(source_file, output_file)

        # Compare with snapshots and collect differences
        differences = []
        matched_files = []

        for actual_file in actual.rglob("*.md"):
            rel_path = self._get_relative_path(actual_file, actual)
            snapshot_file = snapshots / rel_path

            if not snapshot_file.exists():
                differences.append(f"New file: {rel_path}")
                continue

            if filecmp.cmp(actual_file, snapshot_file, shallow=False):
                matched_files.append(actual_file)
            else:
                differences.append(f"Modified: {rel_path}")

        # Check for deleted files (in snapshots but not in actual)
        for snapshot_file in snapshots.rglob("*.md"):
            rel_path = self._get_relative_path(snapshot_file, snapshots)
            actual_file = actual / rel_path
            if not actual_file.exists():
                differences.append(f"Deleted: {rel_path}")

        # Delete matching files
        for file_path in matched_files:
            file_path.unlink()

        # Clean up empty directories
        for dirpath in sorted(actual.rglob("*"), reverse=True):
            if dirpath.is_dir() and not list(dirpath.iterdir()):
                dirpath.rmdir()

        # Assert no differences
        if differences:
            diff_msg = f"Regression test failed for '{suite_name}'. Differences found:\n"
            diff_msg += "\n".join(f"  - {diff}" for diff in differences)
            diff_msg += f"\n\nInspect tests/regression/actual/{suite_name}/ for detailed diffs."
            diff_msg += "\nTo update snapshots: python scripts/update_regression_snapshots.py"
            pytest.fail(diff_msg)
