# Table Embedding Manual

This manual covers table embedding in EmbedM — converting CSV, JSON, and TSV data files into Markdown tables.

## Table of Contents

  - [Overview](#overview)
  - [CSV Tables](#csv-tables)
  - [JSON Tables](#json-tables)
    - [Array of Objects](#array-of-objects)
    - [Selecting Columns](#selecting-columns)
    - [Single Object](#single-object)
  - [TSV Tables](#tsv-tables)
  - [Adding a Title](#adding-a-title)
  - [Format Comparison](#format-comparison)
  - [Complete Property Reference](#complete-property-reference)
  - [Examples in This Manual](#examples-in-this-manual)

## Overview

The `table` embed type converts structured data files into Markdown tables. Instead of maintaining tables by hand, point EmbedM at your data file and it generates a formatted table automatically. When the data changes, recompile and the table updates.

Supported formats:
- **CSV** — comma-separated values
- **JSON** — arrays of objects or single objects
- **TSV** — tab-separated values

## CSV Tables

The simplest table embed takes a CSV file and converts it to Markdown.

**Input:**
```yaml
type: table
source: examples/table_example.csv
```

**Output:**
| name | role | department | location |
| --- | --- | --- | --- |
| Alice | Engineer | Development | New York |
| Bob | Designer | Creative | London |
| Charlie | Manager | Operations | Tokyo |
| Diana | Analyst | Data Science | Berlin |

The first row of the CSV becomes the table header. Quoted fields are handled correctly — commas inside quotes are preserved as cell content, not treated as delimiters.

## JSON Tables

### Array of Objects

The most common JSON structure for tables is an array of objects. Each object becomes a row, and the keys from the first object become column headers.

**Input:**
```yaml
type: table
source: examples/table_example.json
```

**Output:**
| id | endpoint | method | auth |
| --- | --- | --- | --- |
| 1 | /api/users | GET | true |
| 2 | /api/users | POST | true |
| 3 | /api/health | GET | false |
| 4 | /api/docs | GET | false |

Boolean values are displayed as `true`/`false`. Null values become empty cells. Nested objects and arrays are serialized as JSON strings.

### Selecting Columns

Use the `columns` property to choose which columns to include and in what order. This is useful when the JSON contains more fields than you want to show.

**Input:**
```yaml
type: table
source: examples/table_example.json
columns: [endpoint, method, auth]
```

**Output:**
| endpoint | method | auth |
| --- | --- | --- |
| /api/users | GET | true |
| /api/users | POST | true |
| /api/health | GET | false |
| /api/docs | GET | false |

Columns not listed are excluded. The order in `columns` determines the display order.

### Single Object

A JSON file containing a single object (not an array) is converted to a two-column key/value table:

| Key | Value |
| --- | --- |
| name | EmbedM |
| version | 0.4.0 |

## TSV Tables

TSV (tab-separated values) works the same as CSV but uses tabs as delimiters. This format is common in spreadsheet exports and data pipelines.

**Input:**
```yaml
type: table
source: examples/table_example.tsv
```

**Output:**
| name | role | department | location |
| --- | --- | --- | --- |
| Alice | Engineer | Development | New York |
| Bob | Designer | Creative | London |
| Charlie | Manager | Operations | Tokyo |
| Diana | Analyst | Data Science | Berlin |

Quoted fields work the same way as CSV — tabs inside quotes are preserved as cell content.

## Adding a Title

Use the `title` property to display a bold heading above the table. This works with all formats.

**Input:**
```yaml
type: table
source: examples/table_example.csv
title: Team Directory
```

**Output:**
**Team Directory**

| name | role | department | location |
| --- | --- | --- | --- |
| Alice | Engineer | Development | New York |
| Bob | Designer | Creative | London |
| Charlie | Manager | Operations | Tokyo |
| Diana | Analyst | Data Science | Berlin |

## Format Comparison

| Feature | CSV | JSON | TSV |
|---------|-----|------|-----|
| Delimiter | Comma | N/A | Tab |
| Header row | First row | Object keys | First row |
| Quoted fields | Yes | N/A | Yes |
| Column selection | No | Yes (`columns`) | No |
| Nested data | No | Yes (serialized) | No |
| Boolean handling | As-is | `true`/`false` | As-is |

## Complete Property Reference

```yaml
type: table

# Required
source: path/to/data.csv          # File path (relative to markdown file)
                                   # Supported extensions: .csv, .json, .tsv

# Optional
title: "My Table"                  # Bold title displayed above the table
columns: [col1, col2, col3]        # JSON only: select and order columns
```

## Examples in This Manual

This manual itself uses EmbedM. The table of contents at the top was generated with `type: toc`, and all the table examples use `type: table` embeds to convert real data files from the `examples/` directory.
