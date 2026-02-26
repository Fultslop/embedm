from types import SimpleNamespace

str_resources = SimpleNamespace(
    err_query_path_missing_source="'query-path' directive requires a source.",
    err_query_path_unsupported_format="unsupported source format '{ext}'. Supported: json, yaml, yml, xml, toml.",
    err_query_path_invalid_json="invalid JSON: {exc}",
    err_query_path_invalid_yaml="invalid YAML: {exc}",
    err_query_path_invalid_xml="invalid XML: {exc}",
    err_query_path_invalid_toml="invalid TOML: {exc}",
    err_query_path_not_found="path '{path}' not found in '{source}'.",
    err_query_path_format_requires_path="'format' option requires a 'path' to be specified.",
    err_query_path_format_missing_placeholder="'format' option must contain a '{value}' placeholder.",
    err_query_path_format_non_scalar="'format' option cannot be applied to a non-scalar (dict/list) value.",
)
