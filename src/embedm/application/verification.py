from __future__ import annotations

from enum import Enum
from pathlib import Path

from .configuration import Configuration


class VerifyStatus(Enum):
    UP_TO_DATE = "up-to-date"
    STALE = "stale"
    MISSING = "missing"


def apply_line_endings(text: str, line_endings: str) -> str:
    """Normalise output line endings. 'crlf' converts LF→CRLF; 'lf' is a no-op."""
    if line_endings == "crlf":
        return text.replace("\n", "\r\n")
    return text


def verify_file_output(result: str, output_path: str, config: Configuration) -> VerifyStatus:
    """Compare compiled result against the existing file on disk without writing."""
    normalised = apply_line_endings(result, config.line_endings).encode("utf-8")
    path = Path(output_path)
    if not path.exists():
        return VerifyStatus.MISSING
    return VerifyStatus.UP_TO_DATE if path.read_bytes() == normalised else VerifyStatus.STALE
