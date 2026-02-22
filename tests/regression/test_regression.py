"""Regression tests for EmbedM output.

These tests compare processed markdown files against stored snapshots.
To update regression snapshots:
    py .\\src\\embedm\\ .\\tests\\regression\\src\\** -d .\\tests\\regression\\snapshot\\

To update manual snapshots:
    py .\\src\\embedm\\ .\\doc\\manual\\src\\** -d .\\doc\\manual\\compiled\\

"""

import pytest
from pathlib import Path

from embedm.application.config_loader import load_config_file
from embedm.application.configuration import Configuration
from embedm.application.embedm_context import EmbedmContext
from embedm.application.orchestration import _build_directive_sequence
from embedm.application.planner import plan_file
from embedm.domain.plan_node import PlanNode
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_registry import PluginRegistry

_PROJECT_ROOT = Path(__file__).parents[2]

_SRC_DIR = Path(__file__).parent / "src"
_SNAPSHOT_DIR = Path(__file__).parent / "snapshot"
_UPDATE_CMD = "py .\\src\\embedm\\ .\\tests\\regression\\src\\** -d .\\tests\\regression\\snapshot\\"

_MANUAL_SRC_DIR = _PROJECT_ROOT / "doc" / "manual" / "src"
_MANUAL_SNAPSHOT_DIR = _PROJECT_ROOT / "doc" / "manual" / "compiled"
_MANUAL_UPDATE_CMD = "py .\\src\\embedm\\ .\\doc\\manual\\src\\** -d .\\doc\\manual\\compiled\\"


def _build_context(src_dir: Path, config: Configuration) -> EmbedmContext:
    file_cache = FileCache(config.max_file_size, config.max_memory, [str(src_dir)])
    plugin_registry = PluginRegistry()
    plugin_registry.load_plugins(enabled_modules=set(config.plugin_sequence))
    return EmbedmContext(config, file_cache, plugin_registry, accept_all=True)


@pytest.fixture(scope="module")
def context() -> EmbedmContext:
    """Shared EmbedmContext for regression tests."""
    return _build_context(_SRC_DIR, Configuration())


@pytest.fixture(scope="module")
def manual_context() -> EmbedmContext:
    """Shared EmbedmContext for manual regression tests, loaded from the manual config."""
    config, _ = load_config_file(str(_MANUAL_SRC_DIR / "embedm-config.yaml"))
    file_cache = FileCache(config.max_file_size, config.max_memory, [str(_MANUAL_SRC_DIR), str(_PROJECT_ROOT)])
    plugin_registry = PluginRegistry()
    plugin_registry.load_plugins(enabled_modules=set(config.plugin_sequence))
    return EmbedmContext(config, file_cache, plugin_registry, accept_all=True)


def _normalize(text: str, src_dir: Path) -> str:
    """Replace machine-specific paths with a portable placeholder."""
    return text.replace(str(src_dir.resolve()), "<src>")


def _compile(plan_root: PlanNode, context: EmbedmContext, compiled_dir: str = "") -> str:
    """Compile a plan node to string without interactive prompting."""
    if plan_root.document is None:
        return ""
    plugin = context.plugin_registry.find_plugin_by_directive_type(plan_root.directive.type)
    if plugin is None:
        return ""
    plugin_config = PluginConfiguration(
        max_embed_size=context.config.max_embed_size,
        max_recursion=context.config.max_recursion,
        compiled_dir=compiled_dir,
        plugin_sequence=_build_directive_sequence(context.config.plugin_sequence, context.plugin_registry),
    )
    return plugin.transform(plan_root, [], context.file_cache, context.plugin_registry, plugin_config)


def _snapshot_files(snapshot_dir: Path) -> list[Path]:
    return sorted(snapshot_dir.rglob("*.md"))


@pytest.mark.parametrize("snapshot_file", _snapshot_files(_SNAPSHOT_DIR), ids=lambda p: str(p.relative_to(_SNAPSHOT_DIR)))
def test_regression(snapshot_file: Path, context: EmbedmContext) -> None:
    """Process a source file and compare the output against its snapshot."""
    rel_path = snapshot_file.relative_to(_SNAPSHOT_DIR)
    source_file = _SRC_DIR / rel_path

    assert source_file.exists(), f"Source file not found: '{source_file}'. Snapshot may be stale."

    plan_root = plan_file(str(source_file), context)
    actual = _compile(plan_root, context, str(snapshot_file.parent.resolve()))
    expected = snapshot_file.read_text(encoding="utf-8")

    assert _normalize(actual, _SRC_DIR) == _normalize(expected, _SRC_DIR), (
        f"Output mismatch for '{rel_path}'.\n"
        f"To update snapshots:\n  {_UPDATE_CMD}"
    )


@pytest.mark.parametrize(
    "snapshot_file", _snapshot_files(_MANUAL_SNAPSHOT_DIR), ids=lambda p: str(p.relative_to(_MANUAL_SNAPSHOT_DIR))
)
def test_manual_regression(snapshot_file: Path, manual_context: EmbedmContext) -> None:
    """Process a manual source file and compare the output against its compiled snapshot."""
    rel_path = snapshot_file.relative_to(_MANUAL_SNAPSHOT_DIR)
    source_file = _MANUAL_SRC_DIR / rel_path

    assert source_file.exists(), f"Source file not found: '{source_file}'. Snapshot may be stale."

    plan_root = plan_file(str(source_file), manual_context)
    actual = _compile(plan_root, manual_context, str(snapshot_file.parent.resolve()))
    expected = snapshot_file.read_text(encoding="utf-8")

    assert _normalize(actual, _MANUAL_SRC_DIR) == _normalize(expected, _MANUAL_SRC_DIR), (
        f"Output mismatch for '{rel_path}'.\n"
        f"To update snapshots:\n  {_MANUAL_UPDATE_CMD}"
    )
