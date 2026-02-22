FEATURE: TOML support in query-path plugin
========================================
Release v1.0
Created: 22/02/26
Closed: `<date>`
Created by: Claude/FS

## Description

Add `.toml` as a supported source format for the `query-path` directive. Uses `tomllib`
from the Python 3.11+ standard library — no new dependency required.

Related: `feat_add_format_option_to_query_path.md`

## Acceptance criteria

- `source` files with a `.toml` extension are accepted by `validate_directive`
- File content is parsed via a new `normalize_toml.normalize(content: str) -> Any` function
- The resolved value is rendered using the same rules as JSON/YAML/XML (scalar inline, complex as fenced block)
- An unsupported-format error is still raised for any other extension
- Invalid TOML content produces an `err_query_path_invalid_toml` error
- Unit tests cover: valid path resolution, invalid TOML, unsupported extension

## Comments

`tomllib` is read-only (parse only, no write support) which is sufficient here.
tomllib.loads() expects a `str`; the file cache already provides string content.
