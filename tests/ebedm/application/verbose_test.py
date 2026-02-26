"""Tests for verbose mode: console output, planner error messages, and plugin registry tracking."""
from __future__ import annotations

import sys
from importlib.metadata import EntryPoint
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from embedm.application.configuration import Configuration
from embedm.application.console import (
    RunSummary,
    _format_summary,
    _worst_status_label,
    make_cache_event_handler,
    present_run_hint,
    verbose_plan_tree,
    verbose_summary,
    verbose_timing,
)
from embedm.application.embedm_context import EmbedmContext
from embedm.application.planner import create_plan
from embedm.domain.directive import Directive
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_base import PluginBase
from embedm.plugins.plugin_registry import PluginRegistry


# --- RunSummary helpers ---


def test_format_summary_single_file() -> None:
    summary = RunSummary(files_written=1, output_target="out.md", ok_count=1)
    result = _format_summary(summary)
    assert "1 file written" in result
    assert "to out.md" in result
    assert "1 ok" in result


def test_format_summary_plural_files() -> None:
    summary = RunSummary(files_written=3, output_target="./out", ok_count=2, warning_count=1)
    result = _format_summary(summary)
    assert "3 files written" in result
    assert "2 ok" in result
    assert "1 warnings" in result


def test_format_summary_stdout() -> None:
    summary = RunSummary(files_written=0, output_target="stdout")
    result = _format_summary(summary)
    assert "to stdout" in result


# --- _worst_status_label ---


def test_worst_status_label_ok() -> None:
    assert _worst_status_label([Status(StatusLevel.OK, "ok")]) == "OK"


def test_worst_status_label_warning() -> None:
    statuses = [Status(StatusLevel.OK, "ok"), Status(StatusLevel.WARNING, "warn")]
    assert _worst_status_label(statuses) == "WARN"


def test_worst_status_label_error() -> None:
    statuses = [Status(StatusLevel.WARNING, "w"), Status(StatusLevel.ERROR, "e")]
    assert _worst_status_label(statuses) == "ERROR"


def test_worst_status_label_fatal() -> None:
    statuses = [Status(StatusLevel.ERROR, "e"), Status(StatusLevel.FATAL, "f")]
    assert _worst_status_label(statuses) == "FATAL"


# --- verbose_summary ---


def test_verbose_summary_writes_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    summary = RunSummary(files_written=2, output_target="./out", ok_count=2)
    verbose_summary(summary)
    captured = capsys.readouterr()
    assert "embedm process complete" in captured.err
    assert "2 files" in captured.err


# --- present_run_hint ---


def test_present_run_hint_includes_hint(capsys: pytest.CaptureFixture[str]) -> None:
    summary = RunSummary(files_written=1, output_target="out.md", error_count=1)
    present_run_hint(summary)
    captured = capsys.readouterr()
    assert "Use -v 3 or --verbose 3" in captured.err


# --- verbose_plan_tree ---


def test_verbose_plan_tree_ok_node(capsys: pytest.CaptureFixture[str]) -> None:
    node = PlanNode(
        directive=Directive(type="file", source="/path/to/file.md"),
        status=[Status(StatusLevel.OK, "plan created successfully")],
        children=[],
    )
    verbose_plan_tree(node)
    captured = capsys.readouterr()
    assert "[OK]" in captured.err
    assert "/path/to/file.md" in captured.err


def test_verbose_plan_tree_error_node_shows_description(capsys: pytest.CaptureFixture[str]) -> None:
    node = PlanNode(
        directive=Directive(type="file", source="/path/to/file.md"),
        status=[Status(StatusLevel.ERROR, "no plugin registered for directive type 'query-path'")],
        children=[],
    )
    verbose_plan_tree(node)
    captured = capsys.readouterr()
    assert "[ERROR]" in captured.err
    assert "no plugin registered" in captured.err


def test_verbose_plan_tree_child_shows_directive_type(capsys: pytest.CaptureFixture[str]) -> None:
    child = PlanNode(
        directive=Directive(type="query-path", source="/data.json"),
        status=[Status(StatusLevel.OK, "ok")],
        children=[],
    )
    root = PlanNode(
        directive=Directive(type="file", source="/root.md"),
        status=[Status(StatusLevel.OK, "ok")],
        children=[child],
    )
    verbose_plan_tree(root)
    captured = capsys.readouterr()
    assert "query-path" in captured.err
    assert "/data.json" in captured.err


# --- make_cache_event_handler ---


def test_cache_event_handler_miss_includes_timing(capsys: pytest.CaptureFixture[str]) -> None:
    handler = make_cache_event_handler()
    handler("/some/file.md", "miss", 0.042)
    captured = capsys.readouterr()
    assert "cache miss" in captured.err
    assert "0.042s" in captured.err
    assert "/some/file.md" in captured.err


def test_cache_event_handler_hit_no_timing(capsys: pytest.CaptureFixture[str]) -> None:
    handler = make_cache_event_handler()
    handler("/some/file.md", "hit", 0.0)
    captured = capsys.readouterr()
    assert "cache hit" in captured.err
    assert "0.000s" not in captured.err


# --- PluginRegistry discovered/skipped ---


def test_plugin_registry_tracks_discovered_and_skipped() -> None:
    mock_plugin = MagicMock(spec=PluginBase)
    mock_plugin.name = "hello_world"
    mock_plugin.directive_type = "hello_world"
    mock_class = MagicMock(return_value=mock_plugin)

    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "hello_world"
    mock_ep.value = "embedm_plugins.hello_world_plugin:HelloWorldPlugin"
    mock_ep.load.return_value = mock_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]

        registry = PluginRegistry()
        registry.load_plugins(enabled_modules={"embedm_plugins.other_plugin"})

        assert len(registry.discovered) == 1
        assert registry.discovered[0] == ("hello_world", "embedm_plugins.hello_world_plugin")
        assert len(registry.skipped) == 1
        assert registry.skipped[0] == ("hello_world", "embedm_plugins.hello_world_plugin")


def test_plugin_registry_loaded_plugin_not_in_skipped() -> None:
    mock_plugin = MagicMock(spec=PluginBase)
    mock_plugin.name = "hello_world"
    mock_plugin.directive_type = "hello_world"
    mock_class = MagicMock(return_value=mock_plugin)

    mock_ep = MagicMock(spec=EntryPoint)
    mock_ep.name = "hello_world"
    mock_ep.value = "embedm_plugins.hello_world_plugin:HelloWorldPlugin"
    mock_ep.load.return_value = mock_class

    with patch("embedm.plugins.plugin_registry.entry_points") as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]

        registry = PluginRegistry()
        registry.load_plugins(enabled_modules={"embedm_plugins.hello_world_plugin"})

        assert len(registry.discovered) == 1
        assert len(registry.skipped) == 0
        assert registry.count == 1


# --- planner: verbose mode shows available directive types ---


def _make_verbose_context(tmp_path: Path) -> EmbedmContext:
    config = MagicMock()
    config.max_recursion = 10
    config.verbosity = 3
    config.max_embed_size = 0
    file_cache = FileCache(max_file_size=1024, memory_limit=4096, allowed_paths=[str(tmp_path)])
    registry = PluginRegistry()
    return EmbedmContext(config=config, file_cache=file_cache, plugin_registry=registry)


def test_planner_verbose_unknown_type_shows_available(tmp_path: Path) -> None:
    context = _make_verbose_context(tmp_path)
    # register one plugin so 'available' is non-empty
    mock_plugin = MagicMock(spec=PluginBase)
    mock_plugin.name = "file"
    mock_plugin.directive_type = "file"
    mock_plugin.validate_directive.return_value = []
    context.plugin_registry.lookup["file"] = mock_plugin

    plan = create_plan(
        Directive(type="root"),
        "```yaml embedm\ntype: unknown_type\n```\n",
        depth=0,
        context=context,
    )

    error_msgs = [s.description for s in plan.status if s.level == StatusLevel.ERROR]
    assert any("Available:" in msg for msg in error_msgs)
    assert any("file" in msg for msg in error_msgs)


def test_planner_non_verbose_unknown_type_no_available(tmp_path: Path) -> None:
    config = MagicMock()
    config.max_recursion = 10
    config.verbosity = 2
    file_cache = FileCache(max_file_size=1024, memory_limit=4096, allowed_paths=[str(tmp_path)])
    registry = PluginRegistry()
    context = EmbedmContext(config=config, file_cache=file_cache, plugin_registry=registry)

    plan = create_plan(
        Directive(type="root"),
        "```yaml embedm\ntype: unknown_type\n```\n",
        depth=0,
        context=context,
    )

    error_msgs = [s.description for s in plan.status if s.level == StatusLevel.ERROR]
    assert any("no plugin registered" in msg for msg in error_msgs)
    assert not any("Available:" in msg for msg in error_msgs)


# --- timing ---


def test_format_summary_includes_elapsed() -> None:
    summary = RunSummary(files_written=1, output_target="out.md", ok_count=1, elapsed_s=0.312)
    result = _format_summary(summary)
    assert "completed in 0.312s" in result


def test_format_summary_verify_mode_up_to_date() -> None:
    summary = RunSummary(is_verify=True, up_to_date_count=3, stale_count=0, elapsed_s=0.1)
    result = _format_summary(summary)
    assert "verify complete" in result
    assert "3 files checked" in result
    assert "3 up-to-date" in result
    assert "0 stale" in result


def test_format_summary_verify_mode_stale() -> None:
    summary = RunSummary(is_verify=True, up_to_date_count=1, stale_count=2, elapsed_s=0.1)
    result = _format_summary(summary)
    assert "3 files checked" in result
    assert "1 up-to-date" in result
    assert "2 stale" in result


def test_format_summary_verify_mode_singular_file() -> None:
    summary = RunSummary(is_verify=True, up_to_date_count=1, stale_count=0)
    result = _format_summary(summary)
    assert "1 file checked" in result
    assert "files" not in result.split("1 file checked")[0]


def test_verbose_timing_emits_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    verbose_timing("normalize_input", "table", "/data/file.csv", 0.043)
    captured = capsys.readouterr()
    assert "[normalize_input]" in captured.err
    assert "0.043s" in captured.err
    assert "table" in captured.err
    assert "/data/file.csv" in captured.err
