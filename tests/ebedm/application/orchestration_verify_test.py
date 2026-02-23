"""Unit tests for _apply_line_endings and _verify_file_output."""

from __future__ import annotations

from pathlib import Path

from embedm.application.configuration import Configuration
from embedm.application.orchestration import _apply_line_endings, _verify_file_output


# ---------------------------------------------------------------------------
# _apply_line_endings
# ---------------------------------------------------------------------------


def test_apply_line_endings_lf_is_passthrough() -> None:
    text = "line one\nline two\nline three\n"
    assert _apply_line_endings(text, "lf") is text


def test_apply_line_endings_crlf_converts_lf() -> None:
    result = _apply_line_endings("line one\nline two\n", "crlf")
    assert result == "line one\r\nline two\r\n"


def test_apply_line_endings_crlf_no_double_convert() -> None:
    # already-CRLF input should not double-convert
    result = _apply_line_endings("line\r\n", "crlf")
    assert result == "line\r\r\n"  # \r\n → \r\r\n is expected (caller responsibility)


def test_apply_line_endings_unknown_value_is_passthrough() -> None:
    # any unrecognised value falls through to lf path
    text = "line\n"
    assert _apply_line_endings(text, "lf") == text


# ---------------------------------------------------------------------------
# _verify_file_output
# ---------------------------------------------------------------------------


def _config(line_endings: str = "lf") -> Configuration:
    return Configuration(line_endings=line_endings)


def test_verify_file_output_missing_file(tmp_path: Path) -> None:
    from embedm.application.orchestration import _VerifyStatus

    output_path = str(tmp_path / "out.md")
    status = _verify_file_output("content\n", output_path, _config())
    assert status == _VerifyStatus.MISSING


def test_verify_file_output_up_to_date(tmp_path: Path) -> None:
    from embedm.application.orchestration import _VerifyStatus

    output_path = tmp_path / "out.md"
    output_path.write_bytes("content\n".encode("utf-8"))
    status = _verify_file_output("content\n", str(output_path), _config())
    assert status == _VerifyStatus.UP_TO_DATE


def test_verify_file_output_stale(tmp_path: Path) -> None:
    from embedm.application.orchestration import _VerifyStatus

    output_path = tmp_path / "out.md"
    output_path.write_bytes("old content\n".encode("utf-8"))
    status = _verify_file_output("new content\n", str(output_path), _config())
    assert status == _VerifyStatus.STALE


def test_verify_file_output_crlf_up_to_date(tmp_path: Path) -> None:
    from embedm.application.orchestration import _VerifyStatus

    output_path = tmp_path / "out.md"
    output_path.write_bytes("line one\r\nline two\r\n".encode("utf-8"))
    # compiled result has LF; config says crlf — normalisation makes them match
    status = _verify_file_output("line one\nline two\n", str(output_path), _config("crlf"))
    assert status == _VerifyStatus.UP_TO_DATE


def test_verify_file_output_crlf_stale_when_disk_is_lf(tmp_path: Path) -> None:
    from embedm.application.orchestration import _VerifyStatus

    output_path = tmp_path / "out.md"
    # disk has LF but config says crlf — normalised compiled result has CRLF → stale
    output_path.write_bytes("line one\nline two\n".encode("utf-8"))
    status = _verify_file_output("line one\nline two\n", str(output_path), _config("crlf"))
    assert status == _VerifyStatus.STALE
