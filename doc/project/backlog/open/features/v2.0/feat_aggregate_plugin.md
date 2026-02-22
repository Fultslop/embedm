FEATURE: Aggregate plugin
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

A plugin that computes a single aggregate value from a tabular data source (CSV, TSV, or JSON) and embeds it as plain inline text. Complements the `table` plugin, which shows rows; `aggregate` shows a single computed result.

Directive definition:

```yaml embedm
type: aggregate
source: ./sales-data.csv
column: Data_value
function: sum
filter:
  Series_title_1: "Sales (operating income)"
  Period: "2025.09"
format: "NZD {value:.0f}M"
```

### Behaviour

- `source` is required.
- `column` is the column to aggregate (original name, same semantics as table `filter`).
- `function` is one of: `sum`, `count`, `min`, `max`, `avg`.
- `filter` follows the same syntax as the `table` plugin: exact match or operator + value.
- `format` is an optional Python format string with `{value}` as the placeholder. Applied after aggregation.
- Output is plain text with no trailing newline — embeddable inline.
- If no rows match the filter, output is `0` for `sum`/`count` and an error note for `min`/`max`/`avg`.

### Architecture

- Shares the table plugin's data loading and filtering infrastructure (`_load_data`, `_apply_filter`). These should be extracted to a shared module if not already done.
- The aggregate computation is trivial once the filtered rows are available.
- No new dependencies.

## Acceptance criteria

- All five functions (`sum`, `count`, `min`, `max`, `avg`) produce correct results on known data
- `filter` reduces the input set before aggregation
- `format` string is applied correctly; `{value:.2f}` style precision works
- Empty result set: `sum`/`count` return 0; `min`/`max`/`avg` return error note
- Column not found → error caution block
- Non-numeric column with `sum`/`avg`/`min`/`max` → error caution block
- Unit tests and regression example included

## Comments

`22/02/2026 FS/Claude:` The data loading and filtering code in the table plugin should be extracted to a shared utility before or during this implementation to avoid duplication. This also improves the table plugin's testability.
