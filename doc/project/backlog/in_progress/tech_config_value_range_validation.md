TECHNICAL IMPROVEMENT: Add value range validation to config loader
========================================
Created: 21/02/26
Closed: `<date>`
Created by: Claude

## Description

`_parse_config()` in `src/embedm/application/config_loader.py` validates that config keys
exist and have the correct type, but does not validate that values are within a sensible range.

The only cross-field constraint that currently exists is:

```python
if config.max_memory <= config.max_file_size:
    return Configuration(), errors
```

All numeric fields can currently be set to zero, negative, or unreasonably large values without
error. This leads to silent misbehaviour rather than a clear user error:

| Field | Bad value | Effect |
|---|---|---|
| `max_recursion: 0` | user sets 0 | No embed resolves; no error |
| `max_file_size: 0` | user sets 0 | All files rejected silently |
| `max_embed_size: -1` | user sets -1 | Comparison in transformer is undefined |
| `max_recursion: 10000` | user sets 10000 | Stack overflow on deep nesting |

The existing `max_memory > max_file_size` check demonstrates the intended pattern; it just
needs to be applied consistently across all numeric fields.

**Proposed constraints:**

- `max_file_size >= 1`
- `max_recursion >= 1`
- `max_memory > max_file_size` (already checked)
- `max_embed_size >= 0` (0 = disabled, already the documented behaviour)

These constraints should be checked after the field-type validation passes and before
`Configuration()` is constructed. They should produce `StatusLevel.ERROR` and return the
default `Configuration()`, consistent with the existing cross-field check.

String resources for each error message should be added to
`src/embedm/application/application_resources.py`.

## Acceptance criteria

* Setting `max_recursion: 0` in a config file yields a clear ERROR status and falls back to
  default configuration.

* Setting `max_file_size: 0` yields a clear ERROR status.

* Setting `max_embed_size: -1` yields a clear ERROR status.

* Valid edge-case values (`max_embed_size: 0` to disable, `max_recursion: 1`) are accepted
  without error.

* The existing `max_memory <= max_file_size` check is preserved and consolidated alongside the
  new checks.

* Unit tests cover each invalid value case and each valid edge case.

* No failing regression tests.
