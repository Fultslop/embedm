"""Transformer that extracts a line range from compiled content."""

from __future__ import annotations

from dataclasses import dataclass

from embedm.parsing.extraction import extract_line_range


@dataclass
class LineParams:
    """Parameters for line range extraction."""

    content: str
    line_range: str


class LineTransformer:
    """Extracts lines from content using .. range notation."""

    def execute(self, params: LineParams) -> str | None:
        """Return the selected lines as a string, or None if the range is invalid or out of bounds."""
        lines = extract_line_range(params.content, params.line_range)
        return "\n".join(lines) if lines is not None else None
