"""Transformer that extracts a named code symbol from source content."""

from __future__ import annotations

from dataclasses import dataclass

from embedm.parsing.symbol_parser import LanguageConfig, extract_symbol


@dataclass
class SymbolParams:
    """Parameters for symbol extraction."""

    content: str
    symbol_name: str
    config: LanguageConfig


class SymbolTransformer:
    """Extracts a named symbol (class, method, function, etc.) from source content."""

    def execute(self, params: SymbolParams) -> str | None:
        """Return the extracted symbol lines as a string, or None if not found."""
        lines = extract_symbol(params.content, params.symbol_name, params.config)
        return "\n".join(lines) if lines is not None else None
