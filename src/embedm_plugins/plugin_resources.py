from types import SimpleNamespace

# TODO move all user facing strings here
str_resources = SimpleNamespace(
    note_no_toc_content="> [!NOTE]\n> No headings found in document.",
    note_no_results="> [!NOTE]\n> No results.",
    err_table_empty_content="file contains no data rows.",
    err_table_unsupported_format="unsupported file format '{ext}'. Supported: csv, tsv, json.",
    err_table_invalid_json="invalid JSON: {exc}",
    err_table_json_not_array="JSON must be an array of objects, got '{type_name}'.",
    err_table_json_not_objects="JSON array must contain only objects.",
    err_table_column_not_found="column '{col}' not found. Available: {available}.",
    err_table_invalid_select="invalid select expression: '{expr}'.",
    err_table_invalid_order_by="invalid order_by expression: '{expr}'.",
    err_table_invalid_filter_operator="invalid filter operator in '{expr}'. Supported: =, !=, <, <=, >, >=.",
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
