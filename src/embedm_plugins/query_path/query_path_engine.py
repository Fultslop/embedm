from __future__ import annotations

import re
from typing import Any

_SEGMENT_RE = re.compile(r"`[^`]+`|[^.]+")


def parse_path(path: str) -> list[str]:
    """Split a dot-notation path string into segments.

    Backtick-wrapped segments are treated as literal key lookups (e.g. the segment
    ``value`` in the path ``node.`value`.child`` resolves the dict key `` `value` ``
    rather than the reserved XML text-content slot ``value``).
    """
    assert path, "path must be a non-empty string"
    return _SEGMENT_RE.findall(path)


def resolve(tree: Any, segments: list[str]) -> Any:
    """Walk ``tree`` following ``segments`` and return the resolved value.

    Raises KeyError if a dict key is not found or a non-integer segment is used on a list.
    Raises IndexError if an integer list index is out of range.
    """
    assert segments is not None, "segments must not be None"

    node = tree
    for segment in segments:
        if isinstance(node, dict):
            node = _resolve_dict_step(node, segment)
        elif isinstance(node, list):
            node = _resolve_list_step(node, segment)
        else:
            raise KeyError(segment)

    return node


def _resolve_dict_step(node: dict[str, Any], segment: str) -> Any:
    if segment not in node:
        raise KeyError(segment)
    return node[segment]


def _resolve_list_step(node: list[Any], segment: str) -> Any:
    try:
        idx = int(segment)
    except ValueError:
        raise KeyError(segment) from None
    if idx < 0 or idx >= len(node):
        raise IndexError(f"index {idx} out of range (length {len(node)})")
    return node[idx]
