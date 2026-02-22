FEATURE: `format` option for query-path directive
========================================
Release v1.0
Created: 22/02/26
Closed: `<date>`
Created by: Claude/FS

## Description

Add an optional `format` directive option to `query-path` that lets the user wrap the
resolved scalar value in a template string. Without `format`, behaviour is unchanged.

Example usage:

```yaml
type: query-path
source: ./pyproject.toml
path: project.version
format: "version: {value}"
```

Output: `version: 0.6.0`

The placeholder `{value}` is fixed. Python's `str.format_map` is used for substitution,
so the option value is validated to contain exactly one `{value}` token.

`format` only applies when a `path` is specified and the result is a scalar. Applying
`format` to a non-scalar (dict/list) or to a full-document embed (no `path`) is an error.

Related: `feat_add_toml_to_query_path.md`

## Acceptance criteria

- `format` is an optional string option on the `query-path` directive
- `{value}` in the format string is replaced with the resolved scalar
- Missing or invalid `{value}` placeholder in `format` produces a validation error
- Using `format` without `path` produces a validation error
- Using `format` with a non-scalar resolved value produces a validation error
- Without `format`, output is unchanged from current behaviour
- Unit tests cover: basic substitution, missing `{value}`, no `path`, non-scalar value

## Comments

`{value}` was chosen over the last path segment (e.g. `{version}`) to keep the
placeholder unambiguous regardless of path depth and to avoid issues with `.` in
Python format keys.
