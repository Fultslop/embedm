"""Transformer that extracts a named region from compiled content."""

from __future__ import annotations

from dataclasses import dataclass

from embedm.parsing.extraction import extract_region


@dataclass
class RegionParams:
    """Parameters for region extraction."""

    content: str
    region_name: str


class RegionTransformer:
    """Extracts lines between md.start and md.end markers."""

    def execute(self, params: RegionParams) -> str | None:
        """Return the content of the named region, or None if not found."""
        lines = extract_region(params.content, params.region_name)
        return "\n".join(lines) if lines is not None else None
