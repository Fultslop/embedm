"""Transformer that extracts a named region from compiled content."""

from __future__ import annotations

from dataclasses import dataclass, field

from embedm.parsing.extraction import DEFAULT_REGION_END, DEFAULT_REGION_START, extract_region


@dataclass
class RegionParams:
    """Parameters for region extraction."""

    content: str
    region_name: str
    region_start_template: str = field(default=DEFAULT_REGION_START)
    region_end_template: str = field(default=DEFAULT_REGION_END)


class RegionTransformer:
    """Extracts lines between configurable region markers."""

    def execute(self, params: RegionParams) -> str | None:
        """Return the content of the named region, or None if not found."""
        lines = extract_region(
            params.content,
            params.region_name,
            params.region_start_template,
            params.region_end_template,
        )
        return "\n".join(lines) if lines is not None else None
