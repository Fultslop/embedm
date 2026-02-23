# Table Plugin

version 0.6.1

The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting — all declared inline in your markdown.

  - [Basic Usage](#basic-usage)
  - [Selecting Columns](#selecting-columns)
  - [Filtering Rows](#filtering-rows)
    - [Exact match](#exact-match)
    - [Comparison operators](#comparison-operators)
  - [Sorting](#sorting)
  - [Pagination](#pagination)
  - [Display Options](#display-options)
    - [null_string](#null-string)
    - [max_cell_length](#max-cell-length)
  - [Combining Options](#combining-options)

## Basic Usage

Embed a CSV file by specifying `type: table` and a `source` path. Without any other options the full dataset is rendered, so use `limit` on large files.

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
limit: 5
```

| Series_reference | Period | Data_value | Suppressed | STATUS | UNITS | Magnitude | Subject | Group | Series_title_1 | Series_title_2 | Series_title_3 | Series_title_4 | Series_title_5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BDCQ.SF1AA2CA | 2016.06 | 1116.386 |  | F | Dollars | 6 | Business Data Collection - BDC | Industry by financial variable (NZSIOC Level 2) | Sales (operating income) | Forestry and Logging | Current prices | Unadjusted |  |
| BDCQ.SF1AA2CA | 2016.09 | 1070.874 |  | F | Dollars | 6 | Business Data Collection - BDC | Industry by financial variable (NZSIOC Level 2) | Sales (operating income) | Forestry and Logging | Current prices | Unadjusted |  |
| BDCQ.SF1AA2CA | 2016.12 | 1054.408 |  | F | Dollars | 6 | Business Data Collection - BDC | Industry by financial variable (NZSIOC Level 2) | Sales (operating income) | Forestry and Logging | Current prices | Unadjusted |  |
| BDCQ.SF1AA2CA | 2017.03 | 1010.665 |  | F | Dollars | 6 | Business Data Collection - BDC | Industry by financial variable (NZSIOC Level 2) | Sales (operating income) | Forestry and Logging | Current prices | Unadjusted |  |
| BDCQ.SF1AA2CA | 2017.06 | 1233.7 |  | F | Dollars | 6 | Business Data Collection - BDC | Industry by financial variable (NZSIOC Level 2) | Sales (operating income) | Forestry and Logging | Current prices | Unadjusted |  |

## Selecting Columns

Use `select` to project specific columns and give them readable aliases with `as`. Unselected columns are excluded from the output. Column order follows the order in the `select` expression.

The example below keeps only four of the fourteen source columns and renames them:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Series_title_1 as Metric, Series_title_2 as Industry, Data_value as Value_M"
limit: 5
```

| Quarter | Metric | Industry | Value_M |
| --- | --- | --- | --- |
| 2016.06 | Sales (operating income) | Forestry and Logging | 1116.386 |
| 2016.09 | Sales (operating income) | Forestry and Logging | 1070.874 |
| 2016.12 | Sales (operating income) | Forestry and Logging | 1054.408 |
| 2017.03 | Sales (operating income) | Forestry and Logging | 1010.665 |
| 2017.06 | Sales (operating income) | Forestry and Logging | 1233.7 |

## Filtering Rows

Use `filter` to keep only rows that match a set of conditions. Each entry maps a **source column name** to either a bare value (exact match) or an operator followed by a value. Multiple conditions are ANDed together.

Supported operators: `=`, `!=`, `<`, `<=`, `>`, `>=`.

> **Note:** `filter` uses the original column names, even when `select` has renamed them.

### Exact match

Show all quarterly sales figures for a single industry:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Series_title_2: "Forestry and Logging"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Quarter desc"
limit: 8
```

| Quarter | Sales_NZD_M |
| --- | --- |
| 2025.09 | 1433.938 |
| 2025.06 | 1290.178 |
| 2025.03 | 1340.001 |
| 2024.12 | 1362.11 |
| 2024.09 | 1406.142 |
| 2024.06 | 1398.217 |
| 2024.03 | 1483.787 |
| 2023.12 | 1453.065 |

### Comparison operators

Show all entries where the operating profit exceeded 1,000 NZD million in the September 2025 quarter:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Data_value as Profit_NZD_M"
filter:
  Series_title_1: "Operating profit"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
  Data_value: "> 1000"
order_by: "Profit_NZD_M desc"
```

| Industry | Profit_NZD_M |
| --- | --- |
| Professional, Scientific and Technical Services | 3687.021 |
| Rental, Hiring and Real Estate Services | 3486.843 |
| Wholesale Trade | 3130.399 |
| Construction | 2832.017 |
| Electricity, Gas, Water and Waste Services | 2234.229 |
| Transport, Postal and Warehousing | 1762.823 |
| Information Media and Telecommunications | 1399.344 |
| Health Care and Social Assistance | 1394.127 |
| Administrative and Support Services | 1326.075 |
| Food, Beverage and Tobacco Product Manufacturing | 1051.039 |

## Sorting

Use `order_by` to sort by one or more columns. Each column can be `asc` (default) or `desc`. Multiple columns are separated by commas — leftmost is primary sort.

> **Note:** `order_by` uses aliased column names (after `select` has been applied).

Top five industries by sales in the September 2025 quarter, unadjusted current prices:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Data_value as Sales_NZD_M"
filter:
  Series_title_1: "Sales (operating income)"
  Period: "2025.09"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
order_by: "Sales_NZD_M desc"
limit: 5
```

| Industry | Sales_NZD_M |
| --- | --- |
| Wholesale Trade | 40357.511 |
| Retail Trade | 24673.449 |
| Construction | 23138.631 |
| Professional, Scientific and Technical Services | 15932.94 |
| Food, Beverage and Tobacco Product Manufacturing | 15683.22 |

## Pagination

Use `limit` to cap the number of rows and `offset` to skip rows from the top. Together they allow stepping through a dataset in pages.

Page 1 — first five entries for Wholesale Trade sales:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
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

| Quarter | Sales_NZD_M |
| --- | --- |
| 2016.06 | 23406.009 |
| 2016.09 | 23994.212 |
| 2016.12 | 25705.259 |
| 2017.03 | 23310.026 |
| 2017.06 | 24840.66 |

Page 2 — next five:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
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

| Quarter | Sales_NZD_M |
| --- | --- |
| 2017.09 | 25475.251 |
| 2017.12 | 27896.872 |
| 2018.03 | 24728.334 |
| 2018.06 | 26645.783 |
| 2018.09 | 27695.288 |

## Display Options

### null_string

Rows with a `STATUS` of `C` (confidential) have no `Data_value`. Use `null_string` to replace empty cells with a readable placeholder:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
select: "Period as Quarter, Series_title_2 as Industry, Series_title_1 as Metric, Data_value as Value_M"
filter:
  STATUS: "C"
null_string: "–"
limit: 6
```

| Quarter | Industry | Metric | Value_M |
| --- | --- | --- | --- |
| 2016.06 | Retail Trade | Sales (operating income) | – |
| 2016.09 | Retail Trade | Sales (operating income) | – |
| 2016.12 | Retail Trade | Sales (operating income) | – |
| 2017.03 | Retail Trade | Sales (operating income) | – |
| 2017.06 | Retail Trade | Sales (operating income) | – |
| 2016.06 | Retail Trade | Sales (operating income) | – |

### max_cell_length

Long cell values can make tables unwieldy. `max_cell_length` truncates any cell that exceeds the given character count, appending `…`. This is useful when column content varies widely in length.

The industry names in this dataset reach 60+ characters. Truncating at 30 keeps the table compact:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
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

| Industry | Quarter | Sales_NZD_M |
| --- | --- | --- |
| Wholesale Trade | 2025.09 | 40357.511 |
| Retail Trade | 2025.09 | 24673.449 |
| Construction | 2025.09 | 23138.631 |
| Professional, Scientific and … | 2025.09 | 15932.94 |
| Food, Beverage and Tobacco Pr… | 2025.09 | 15683.22 |
| Transport, Postal and Warehou… | 2025.09 | 10344.189 |
| Rental, Hiring and Real Estat… | 2025.09 | 9300.489 |
| Electricity, Gas, Water and W… | 2025.09 | 7905.904 |

## Combining Options

All options compose freely. This example answers the question *"what were the five highest salary bills among NZ industries in recent quarters?"* using select, filter, sort, and limit together:

```yaml
type: table
source: ./business-financial-data-september-2025-quarter.csv
select: "Series_title_2 as Industry, Period as Quarter, Data_value as Salaries_NZD_M"
filter:
  Series_title_1: "Salaries and wages"
  Series_title_3: "Current prices"
  Series_title_4: "Unadjusted"
  Data_value: "> 3000"
order_by: "Salaries_NZD_M desc, Quarter desc"
limit: 5
```

| Industry | Quarter | Salaries_NZD_M |
| --- | --- | --- |
| Professional, Scientific and Technical Services | 2024.12 | 5001.706 |
| Professional, Scientific and Technical Services | 2024.06 | 4952.352 |
| Professional, Scientific and Technical Services | 2024.09 | 4943.576 |
| Professional, Scientific and Technical Services | 2023.12 | 4932.693 |
| Professional, Scientific and Technical Services | 2025.06 | 4913.125 |
