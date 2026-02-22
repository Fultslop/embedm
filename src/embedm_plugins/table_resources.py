from types import SimpleNamespace

str_resources = SimpleNamespace(
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
)
