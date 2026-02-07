"""Region and line extraction utilities."""

import re
from typing import Optional, Dict


def extract_region(content: str, tag_name: str) -> Optional[Dict]:
    """
    Extracts a specific region marked by md.start:tagName and md.end:tagName
    Returns {'lines': list[str], 'startLine': int} or None
    """
    lines = content.replace('\r\n', '\n').split('\n')
    start_marker = f"md.start:{tag_name.strip()}"
    end_marker = f"md.end:{tag_name.strip()}"

    def normalize_marker(s):
        return re.sub(r'\s', '', s)

    start_index = -1
    end_index = -1

    for i, line in enumerate(lines):
        clean_line = normalize_marker(line)
        if normalize_marker(start_marker) in clean_line:
            start_index = i + 1
        elif normalize_marker(end_marker) in clean_line:
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
    Extracts a range of lines based on L<start>-<end> syntax
    Returns {'lines': list[str], 'startLine': int} or None
    """
    lines = content.replace('\r\n', '\n').split('\n')

    # Handles L10, L10-20, L10-, and L10-L20
    match = re.match(r'^L(\d+)(?:-L?(\d+)?)?$', range_str, re.IGNORECASE)

    if not match:
        return None

    start_line = int(match.group(1))
    has_dash = '-' in range_str
    # If there's a dash but no second number (L10-), go to the end
    end_line_param = int(match.group(2)) if match.group(2) else (len(lines) if has_dash else start_line)

    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line_param)

    return {
        'lines': lines[start_idx:end_idx],
        'startLine': start_line
    }
