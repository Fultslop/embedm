from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

_RESERVED_KEYS: frozenset[str] = frozenset({"attributes", "value"})


def normalize(content: str) -> dict[str, Any]:
    """Parse XML content into a normalised Python dict. Raises ET.ParseError on invalid input.

    Element attributes are stored under the reserved key ``attributes``.
    Element text content is stored under the reserved key ``value``.
    Child elements whose tag collides with a reserved key are stored with the tag wrapped in
    backticks (e.g. a child named ``value`` is stored as the key `` `value` ``).
    Multiple child elements sharing the same tag are stored as a list.
    """
    root = ET.fromstring(content)
    return {root.tag: _normalize_element(root)}


def _normalize_element(element: ET.Element) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if element.attrib:
        result["attributes"] = dict(element.attrib)

    text = element.text.strip() if element.text else ""
    if text:
        result["value"] = text

    children_by_tag: dict[str, list[ET.Element]] = {}
    for child in element:
        children_by_tag.setdefault(child.tag, []).append(child)

    for tag, children in children_by_tag.items():
        key = f"`{tag}`" if tag in _RESERVED_KEYS else tag
        normalized = [_normalize_element(c) for c in children]
        result[key] = normalized[0] if len(normalized) == 1 else normalized

    return result
