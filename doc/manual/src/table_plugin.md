# Table Plugin

```yaml embedm
type: query-path
source: ../../../pyproject.toml
path: project.version
format: "version {value}"
```

The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown.

```yaml embedm
type: toc
add_slugs: True
```

## Basic Usage

Embed a CSV file by specifying `type: table` and a `source` path. Without any other options the full dataset is rendered, so use `limit` on large files.

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
limit: 5
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
limit: 5
```

## Selecting Columns

Use `select` to project specific columns and give them readable aliases with `as`. Unselected columns are excluded from the output. Column order follows the order in the `select` expression.

The example below keeps only four of the fourteen source columns and renames them:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Series_title_1 as Metric, Series_title_2 as Industry, Data_value as Value_M"
limit: 5
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Series_title_1 as Metric, Series_title_2 as Industry, Data_value as Value_M"
limit: 5
```

## Filtering Rows

Use `filter` to keep only rows that match a set of conditions. Each entry maps a **source column name** to either a bare value (exact match) or an operator followed by a value. Multiple conditions are ANDed together.

Supported operators: `=`, `!=`, `<`, `<=`, `>`, `>=`.

> **Note:** `filter` uses the original column names, even when `select` has renamed them.

### Exact match

Show all quarterly sales figures for a single industry:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Forestry and Logging"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter desc"
limit: 8
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Forestry and Logging"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter desc"
limit: 8
```

### Comparison operators

Show all entries where the operating profit exceeded 1,000 NZD million in the September 2025 quarter:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Data_value as Profit_NZD_M"
filter:
  Series_title_1: "Operating profit"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
  Data_value: "> 1000"
order_by: "Profit_NZD_M desc"
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Data_value as Profit_NZD_M"
filter:
  Series_title_1: "Operating profit"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
  Data_value: "> 1000"
order_by: "Profit_NZD_M desc"
```

## Sorting

Use `order_by` to sort by one or more columns. Each column can be `asc` (default) or `desc`. Multiple columns are separated by commas — leftmost is primary sort.

> **Note:** `order_by` uses aliased column names (after `select` has been applied).

Top five industries by sales in the September 2025 quarter, unadjusted current prices:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Sales_NZD_M desc"
limit: 5
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Sales_NZD_M desc"
limit: 5
```

## Pagination

Use `limit` to cap the number of rows and `offset` to skip rows from the top. Together they allow stepping through a dataset in pages.

Page 1 — first five entries for Wholesale Trade sales:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Wholesale Trade"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter asc"
limit: 5
offset: 0
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Wholesale Trade"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter asc"
limit: 5
offset: 0
```

Page 2 — next five:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Wholesale Trade"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter asc"
limit: 5
offset: 5
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Wholesale Trade"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter asc"
limit: 5
offset: 5
```

## Display Options

### null_string

Rows with a `STATUS` of `C` (confidential) have no `Data_value`. Use `null_string` to replace empty cells with a readable placeholder:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Series_title_2 as Industry, Series_title_1 as Metric, Data_value as Value_M"
filter:
  STATUS: "C"
null_string: "–"
limit: 6
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Series_title_2 as Industry, Series_title_1 as Metric, Data_value as Value_M"
filter:
  STATUS: "C"
null_string: "–"
limit: 6
```

### max_cell_length

Long cell values can make tables unwieldy. `max_cell_length` truncates any cell that exceeds the given character count, appending `…`. This is useful when column content varies widely in length.

The industry names in this dataset reach 60+ characters. Truncating at 30 keeps the table compact:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Sales_NZD_M desc"
max_cell_length: 30
limit: 8
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Sales_NZD_M desc"
max_cell_length: 30
limit: 8
```

## Combining Options

All options compose freely. This example answers the question *"what were the five highest salary bills among NZ industries in recent quarters?"* using select, filter, sort, and limit together:

```yaml
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Period as Quarter, Data_value as Salaries_NZD_M"
filter:
  Series_title_1: "Salaries and wages"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
  Data_value: "> 3000"
order_by: "Salaries_NZD_M desc, Quarter desc"
limit: 5
```

```yaml embedm
type: table
source: ./assets/tables/business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Period as Quarter, Data_value as Salaries_NZD_M"
filter:
  Series_title_1: "Salaries and wages"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
  Data_value: "> 3000"
order_by: "Salaries_NZD_M desc, Quarter desc"
limit: 5
```
