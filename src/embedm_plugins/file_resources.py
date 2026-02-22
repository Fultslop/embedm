from types import SimpleNamespace

str_resources = SimpleNamespace(
    err_embed_size_exceeded="embedded content exceeds max_embed_size ({limit} bytes).",
    err_file_exclusive_options="only one of 'region', 'lines', or 'symbol' may be specified.",
    err_file_invalid_line_range="invalid 'lines' value '{range}'. Expected: 10, 5..10, 10.., or ..10.",
    err_file_symbol_unsupported_ext="symbol extraction is not supported for '{ext}' files.",
    err_file_region_not_found="region '{region}' not found in '{source}'.",
    err_file_symbol_not_found="symbol '{symbol}' not found in '{source}'.",
)


def render_error_note(messages: list[str]) -> str:
    """Render a list of error messages as a GFM caution block."""
    lines = ["> [!CAUTION]"] + [f"> **embedm:** {msg}" for msg in messages]
    return "\n".join(lines) + "\n"
