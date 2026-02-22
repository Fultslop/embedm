"""Line range and named region extraction from text content."""

from __future__ import annotations

import re

DEFAULT_REGION_START = "md.start:{tag}"
DEFAULT_REGION_END = "md.end:{tag}"

_REGION_COMMENT_PREFIX = r"(?:#|//|<!--|/\*)"


def _compile_region_pattern(template: str) -> re.Pattern[str]:
    """Build a region marker regex from a template containing {tag}.

    The text before {tag} is treated as a literal prefix (after the comment character).
    Example: "md.start:{tag}" → matches lines like "# md.start: myregion".
    """
    prefix = template.split("{tag}")[0]
    return re.compile(
        r"^\s*" + _REGION_COMMENT_PREFIX + r"\s*" + re.escape(prefix) + r"\s*(?P<name>\S+)",
        re.IGNORECASE,
    )


_REGION_START = _compile_region_pattern(DEFAULT_REGION_START)
_REGION_END = _compile_region_pattern(DEFAULT_REGION_END)

_SINGLE_LINE = re.compile(r"^\d+$")
_LINE_RANGE = re.compile(r"^(\d*)\.\.(\d*)$")


def _matches_region(line: str, name: str, pattern: re.Pattern[str]) -> bool:
    m = pattern.match(line)
    return bool(m and m.group("name") == name)


def extract_region(
    content: str,
    region_name: str,
    start_template: str = DEFAULT_REGION_START,
    end_template: str = DEFAULT_REGION_END,
) -> list[str] | None:
    """Extract lines between region start and end markers.

    Markers must appear inside a comment (lines starting with #, //, <!--, or /*).
    The marker format is controlled by start_template and end_template, which must
    contain {tag} as a placeholder for the region name.
    Returns the lines between the markers (exclusive of marker lines), or None if
    the region is not found or is not properly terminated.
    """
    start_pat = _REGION_START if start_template == DEFAULT_REGION_START else _compile_region_pattern(start_template)
    end_pat = _REGION_END if end_template == DEFAULT_REGION_END else _compile_region_pattern(end_template)

    lines = content.replace("\r\n", "\n").split("\n")
    name = region_name.strip()
    start_idx: int = -1

    for i, line in enumerate(lines):
        if start_idx == -1:
            if _matches_region(line, name, start_pat):
                start_idx = i + 1
        else:
            if _matches_region(line, name, end_pat):
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
