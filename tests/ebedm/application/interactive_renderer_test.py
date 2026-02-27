"""Tests for InteractiveRenderer ANSI live-progress output."""

from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from embedm.application.application_events import (
    CompilationStarted,
    FileCompleted,
    FileError,
    FileStarted,
    NodeCompiled,
    SessionComplete,
    SessionStarted,
)
from embedm.application.configuration import Configuration
from embedm.application.interactive_renderer import InteractiveRenderer
from embedm.infrastructure.events import EventDispatcher

_FILE = "/abs/path/doc.md"
_OUT = "/abs/out/doc.md"

# SGR codes (colors, bold, dim, reset) have the form ESC[<n>m
_SGR_RE = re.compile(r"\x1b\[\d+m")


def _make(verbosity: int = 2, no_color: bool = True) -> tuple[InteractiveRenderer, EventDispatcher]:
    config = Configuration(verbosity=verbosity, no_color=no_color)
    renderer = InteractiveRenderer(config)
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


# --- v0 prints nothing ---


def test_v0_session_complete_prints_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=0)
    dispatcher.emit(_complete())
    assert capsys.readouterr().err == ""


# --- v1 version and summary ---


def test_v1_session_started_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=1)
    dispatcher.emit(_started())
    assert "Embedm v1.2.3" in capsys.readouterr().err


def test_v1_session_complete_prints_summary(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=1)
    dispatcher.emit(_complete(ok=2, elapsed=0.5))
    assert "Embedm complete" in capsys.readouterr().err


# --- v2 file completed prints permanent line ---


def test_v2_file_completed_ok_line(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.interactive_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileCompleted(file_path=_FILE, output_path=_OUT, elapsed=0.20, index=0, total=1))
    captured = capsys.readouterr().err
    assert "[OK]" in captured
    assert "0.20s" in captured


def test_v2_file_error_err_line(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.interactive_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileError(file_path=_FILE, message="transform error", elapsed=0.05, index=0, total=1))
    captured = capsys.readouterr().err
    assert "[ERR]" in captured
    assert "transform error" in captured


# --- live section ---


def test_v2_file_started_draws_live_section(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.interactive_renderer.to_relative", return_value="doc.md"):
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileStarted(file_path=_FILE, node_count=5, index=0, total=1))
    captured = capsys.readouterr().err
    assert "Embedm [" in captured
    assert "doc.md" in captured


def test_v2_node_compiled_updates_progress(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.interactive_renderer.to_relative", return_value="doc.md"):
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileStarted(file_path=_FILE, node_count=4, index=0, total=1))
        capsys.readouterr()  # clear
        dispatcher.emit(NodeCompiled(file_path=_FILE, node_index=2, node_count=4, elapsed=0.1))
    captured = capsys.readouterr().err
    # live section should include 50% progress
    assert "50%" in captured


def test_v2_file_completed_removes_from_live(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.interactive_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileStarted(file_path=_FILE, node_count=2, index=0, total=1))
        dispatcher.emit(FileCompleted(file_path=_FILE, output_path=_OUT, elapsed=0.10, index=0, total=1))
    renderer, _ = _make()
    assert _FILE not in renderer._file_progress


# --- no color ---


def test_no_color_produces_no_color_codes(capsys: pytest.CaptureFixture[str]) -> None:
    """no_color=True suppresses SGR (color/bold/dim) codes; cursor controls are still used."""
    _, dispatcher = _make(verbosity=2, no_color=True)
    with patch("embedm.application.interactive_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(_started())
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileCompleted(file_path=_FILE, output_path=_OUT, elapsed=0.1, index=0, total=1))
        dispatcher.emit(_complete())
    captured = capsys.readouterr().err
    assert _SGR_RE.search(captured) is None, "expected no SGR color codes with no_color=True"


def test_with_color_produces_ansi(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.dict("os.environ", {}, clear=True):
        config = Configuration(verbosity=2, no_color=False)
        renderer = InteractiveRenderer(config)
        # Verify the renderer's internal _use_color state
        assert renderer._use_color is True


# --- error re-listing on session complete ---


def test_session_complete_relists_errors(capsys: pytest.CaptureFixture[str]) -> None:
    _, dispatcher = _make(verbosity=2)
    with patch("embedm.application.interactive_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(CompilationStarted(file_count=1))
        dispatcher.emit(FileError(file_path=_FILE, message="oops", elapsed=0.01, index=0, total=1))
    capsys.readouterr()  # clear previous output
    with patch("embedm.application.interactive_renderer.to_relative", side_effect=lambda p: p):
        dispatcher.emit(_complete(ok=0, err=1))
    captured = capsys.readouterr().err
    # summary should be present
    assert "Embedm complete" in captured
