"""Tests for StreamRenderer plain-text output behaviour per verbosity level."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from embedm.application.application_events import (
    FileCompleted,
    FileError,
    FilePlanError,
    FilePlanned,
    PlanningStarted,
    PluginsLoaded,
    SessionComplete,
    SessionStarted,
)
from embedm.application.configuration import Configuration
from embedm.application.stream_renderer import StreamRenderer
from embedm.infrastructure.events import EventDispatcher

_FILE = "/abs/path/test_file.md"
_OUT = "/abs/out/test_file.md"


def _make(verbosity: int = 2) -> tuple[StreamRenderer, EventDispatcher]:
    config = Configuration(verbosity=verbosity)
    renderer = StreamRenderer(config)
    dispatcher = EventDispatcher()
    renderer.subscribe(dispatcher)
    return renderer, dispatcher


def _started() -> SessionStarted:
    return SessionStarted(
        version="1.2.3",
        config_source="embedm-config.yaml",
        input_type="directory",
        output_type="directory",
    )


def _complete(ok: int = 1, err: int = 0, elapsed: float = 1.5) -> SessionComplete:
    return SessionComplete(ok_count=ok, error_count=err, total_elapsed=elapsed)


# --- verbosity 0 ---


def test_v0_session_start_prints_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=0)
    dispatcher.emit(_started())
    assert capsys.readouterr().err == ""


def test_v0_session_complete_prints_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=0)
    dispatcher.emit(_complete())
    assert capsys.readouterr().err == ""


# --- verbosity 1 ---


def test_v1_session_started_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=1)
    dispatcher.emit(_started())
    assert "Embedm v1.2.3" in capsys.readouterr().err


def test_v1_no_config_labels(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=1)
    dispatcher.emit(_started())
    captured = capsys.readouterr().err
    assert "Config:" not in captured
    assert "Input:" not in captured
    assert "Output:" not in captured


def test_v1_session_complete_prints_summary(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=1)
    dispatcher.emit(_complete(ok=2, elapsed=0.5))
    assert "Embedm complete" in capsys.readouterr().err


def test_v1_no_file_completion_lines(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=1)
    with patch("embedm.application.stream_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(FileCompleted(file_path=_FILE, output_path=_OUT, elapsed=0.1, index=0, total=1))
    assert capsys.readouterr().err == ""


# --- verbosity 2 ---


def test_v2_config_labels(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    dispatcher.emit(_started())
    captured = capsys.readouterr().err
    assert "Config:" in captured
    assert "Input:" in captured
    assert "Output:" in captured


def test_v2_planning_started(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    dispatcher.emit(PlanningStarted(file_count=5))
    assert "Planning 5 file(s)" in capsys.readouterr().err


def test_v2_file_planned_shows_path(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.stream_renderer.to_relative", return_value="rel/path.md"):
        dispatcher.emit(FilePlanned(file_path=_FILE, index=0, total=3))
    captured = capsys.readouterr().err
    assert "[1/3]" in captured
    assert "rel/path.md" in captured


def test_v2_file_plan_error_shows_err(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.stream_renderer.to_relative", return_value="rel/path.md"):
        dispatcher.emit(FilePlanError(file_path=_FILE, index=1, total=3, message="bad directive"))
    captured = capsys.readouterr().err
    assert "[ERR]" in captured
    assert "bad directive" in captured


def test_v2_file_completed_ok_line(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.stream_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(FileCompleted(file_path=_FILE, output_path=_OUT, elapsed=0.12, index=0, total=1))
    captured = capsys.readouterr().err
    assert "[OK]" in captured
    assert "0.12s" in captured


def test_v2_file_error_err_line(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.stream_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(FileError(file_path=_FILE, message="compilation failed", elapsed=0.05, index=0, total=1))
    captured = capsys.readouterr().err
    assert "[ERR]" in captured
    assert "compilation failed" in captured


def test_v2_plugins_loaded_prints_count(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    dispatcher.emit(PluginsLoaded(discovered=3, loaded=3, errors=[]))
    assert "3 plugins discovered" in capsys.readouterr().err


def test_v2_plugin_errors_always_print(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=0)
    dispatcher.emit(PluginsLoaded(discovered=1, loaded=0, errors=["plugin X failed"]))
    captured = capsys.readouterr().err
    assert "[ERR]" in captured
    assert "plugin X failed" in captured


def test_v2_summary_contains_total_time(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    dispatcher.emit(_complete(ok=3, elapsed=2.0))
    assert "total time: 2.0s" in capsys.readouterr().err
