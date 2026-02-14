"""Region and line extraction utilities."""

import re
from typing import Optional, Dict


def extract_region(content: str, tag_name: str) -> Optional[Dict]:
    """
    Extracts a specific region marked by md.start:tagName and md.end:tagName
    Returns {'lines': list[str], 'startLine': int} or None

    Markers must be in comments (lines starting with #, //, etc.) to avoid
    matching mentions of markers in docstrings or regular text.
    """
    lines = content.replace('\r\n', '\n').split('\n')
    tag_name_clean = tag_name.strip()

    # Regex pattern to match region markers in comments
    # Matches: # md.start:name or // md.start:name or <!-- md.start:name -->
    # Allows optional whitespace after colon and comment markers
    start_pattern = re.compile(
        r'^\s*(?:#|//|<!--|/\*)\s*md\.start\s*:\s*' + re.escape(tag_name_clean) + r'\b',
        re.IGNORECASE
    )
    end_pattern = re.compile(
        r'^\s*(?:#|//|<!--|/\*)\s*md\.end\s*:\s*' + re.escape(tag_name_clean) + r'\b',
        re.IGNORECASE
    )

    start_index = -1
    end_index = -1

    for i, line in enumerate(lines):
        if start_pattern.match(line):
            start_index = i + 1
        elif end_pattern.match(line):
            end_index = i
            break

    if start_index == -1 or end_index == -1:
        return None

    return {
        'lines': lines[start_index:end_index],
        'startLine': start_index + 1
    }


def extract_lines(content: str, range_str: str) -> Optional[Dict]:
    """
    Extracts a range of lines based on numeric range syntax.

    Supports formats:
    - "10-20" - lines 10 through 20
    - "15" - just line 15
    - "10-" - line 10 to end of file
    - "L10-20" - legacy format (for backward compatibility with 'region' property)

    Returns {'lines': list[str], 'startLine': int} or None
    """
    lines = content.replace('\r\n', '\n').split('\n')

    # Try new format first: 10, 10-20, 10-
    match = re.match(r'^(\d+)(?:-(\d+)?)?$', range_str)

    # Fall back to legacy L-prefix format: L10, L10-20, L10-, L10-L20
    if not match:
        match = re.match(r'^L(\d+)(?:-L?(\d+)?)?$', range_str, re.IGNORECASE)

    if not match:
        return None

    start_line = int(match.group(1))
    has_dash = '-' in range_str
    # If there's a dash but no second number (10- or L10-), go to the end
    end_line_param = int(match.group(2)) if match.group(2) else (len(lines) if has_dash else start_line)

    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line_param)

    return {
        'lines': lines[start_idx:end_idx],
        'startLine': start_line
    }
