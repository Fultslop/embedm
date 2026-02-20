"""Line range and named region extraction from text content."""

from __future__ import annotations

import re

_REGION_COMMENT_PREFIX = r"(?:#|//|<!--|/\*)"
_REGION_START = re.compile(
    r"^\s*" + _REGION_COMMENT_PREFIX + r"\s*md\.start\s*:\s*(?P<name>\S+)",
    re.IGNORECASE,
)
_REGION_END = re.compile(
    r"^\s*" + _REGION_COMMENT_PREFIX + r"\s*md\.end\s*:\s*(?P<name>\S+)",
    re.IGNORECASE,
)

_SINGLE_LINE = re.compile(r"^\d+$")
_LINE_RANGE = re.compile(r"^(\d*)\.\.(\d*)$")


def _matches_region(line: str, name: str, pattern: re.Pattern[str]) -> bool:
    m = pattern.match(line)
    return bool(m and m.group("name") == name)


def extract_region(content: str, region_name: str) -> list[str] | None:
    """Extract lines between md.start and md.end markers.

    Markers must appear inside a comment (lines starting with #, //, <!--, or /*).
    Returns the lines between the markers (exclusive of marker lines), or None if
    the region is not found or is not properly terminated.
    """
    lines = content.replace("\r\n", "\n").split("\n")
    name = region_name.strip()
    start_idx: int = -1

    for i, line in enumerate(lines):
        if start_idx == -1:
            if _matches_region(line, name, _REGION_START):
                start_idx = i + 1
        else:
            if _matches_region(line, name, _REGION_END):
                return lines[start_idx:i]

    return None


def _parse_line_range_bounds(m: re.Match[str], total: int) -> tuple[int, int]:
    start = int(m.group(1)) if m.group(1) else 1
    end = int(m.group(2)) if m.group(2) else total
    return start, end


def _is_range_valid(start: int, end: int, total: int) -> bool:
    return 1 <= start <= total and start <= end


def extract_line_range(content: str, range_str: str) -> list[str] | None:
    """Extract a range of lines using .. notation.

    Supported formats: '10' (single line), '5..10' (inclusive range),
    '10..' (from line to end), '..10' (from start to line). Line numbers are 1-based.
    Returns the selected lines, or None if the format is unrecognised or out of bounds.
    """
    lines = content.replace("\r\n", "\n").split("\n")
    total = len(lines)

    if _SINGLE_LINE.fullmatch(range_str):
        n = int(range_str)
        return lines[n - 1 : n] if 1 <= n <= total else None

    m = _LINE_RANGE.fullmatch(range_str)
    if not m:
        return None

    start, end = _parse_line_range_bounds(m, total)
    if not _is_range_valid(start, end, total):
        return None

    return lines[start - 1 : end]


def is_valid_line_range(range_str: str) -> bool:
    """Return True if range_str is a syntactically valid line range expression."""
    return bool(_SINGLE_LINE.fullmatch(range_str) or _LINE_RANGE.fullmatch(range_str))
