"""Regression tests for EmbedM output.

These tests compare processed markdown files against stored snapshots.
To update snapshots, run:
    py .\\src\\embedm\\ .\\tests\\regression\\src\\** -d .\\tests\\regression\\snapshot\\

"""

import pytest
from pathlib import Path

from embedm.application.configuration import Configuration
from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import plan_file
from embedm.domain.plan_node import PlanNode
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry


_SRC_DIR = Path(__file__).parent / "src"
_SNAPSHOT_DIR = Path(__file__).parent / "snapshot"
_UPDATE_CMD = "py .\\src\\embedm\\ .\\tests\\regression\\src\\** -d .\\tests\\regression\\snapshot\\"


@pytest.fixture(scope="module")
def context() -> EmbedmContext:
    """Shared EmbedmContext for all regression tests."""
    config = Configuration()
    file_cache = FileCache(config.max_file_size, config.max_memory, [str(_SRC_DIR)])
    plugin_registry = PluginRegistry()
    plugin_registry.load_plugins(enabled_modules=set(config.plugin_sequence))
    return EmbedmContext(config, file_cache, plugin_registry, accept_all=True)


def _normalize(text: str) -> str:
    """Replace machine-specific paths with a portable placeholder."""
    return text.replace(str(_SRC_DIR.resolve()), "<src>")


def _compile(plan_root: PlanNode, context: EmbedmContext) -> str:
    """Compile a plan node to string without interactive prompting."""
    if plan_root.document is None:
        return ""
    plugin = context.plugin_registry.find_plugin_by_directive_type(plan_root.directive.type)
    if plugin is None:
        return ""
    return plugin.transform(plan_root, [], context.file_cache, context.plugin_registry)


def _snapshot_files() -> list[Path]:
    return sorted(_SNAPSHOT_DIR.rglob("*.md"))


@pytest.mark.parametrize("snapshot_file", _snapshot_files(), ids=lambda p: str(p.relative_to(_SNAPSHOT_DIR)))
def test_regression(snapshot_file: Path, context: EmbedmContext) -> None:
    """Process a source file and compare the output against its snapshot."""
    rel_path = snapshot_file.relative_to(_SNAPSHOT_DIR)
    source_file = _SRC_DIR / rel_path

    assert source_file.exists(), f"Source file not found: '{source_file}'. Snapshot may be stale."

    plan_root = plan_file(str(source_file), context)
    actual = _compile(plan_root, context)
    expected = snapshot_file.read_text(encoding="utf-8")

    assert _normalize(actual) == _normalize(expected), (
        f"Output mismatch for '{rel_path}'.\n"
        f"To update snapshots:\n  {_UPDATE_CMD}"
    )
