from __future__ import annotations

from enum import Enum
from pathlib import Path

from embedm.infrastructure.file_util import apply_line_endings

from .configuration import Configuration


class VerifyStatus(Enum):
    UP_TO_DATE = "up-to-date"
    STALE = "stale"
    MISSING = "missing"


def verify_file_output(result: str, output_path: str, config: Configuration) -> VerifyStatus:
    """Compare compiled result against the existing file on disk without writing."""
    normalised = apply_line_endings(result, config.line_endings).encode("utf-8")
    path = Path(output_path)
    if not path.exists():
        return VerifyStatus.MISSING
    return VerifyStatus.UP_TO_DATE if path.read_bytes() == normalised else VerifyStatus.STALE
