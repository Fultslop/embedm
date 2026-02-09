# Table Line Numbers Test

This tests file embedding with table-formatted line numbers (GitHub-compatible).

## Full File with Table Line Numbers

```yaml embedm
type: file
source: data/sample.py
line_numbers: table
```

## Specific Region with Table Line Numbers

```yaml embedm
type: file
source: data/sample.py
lines: L4-13
line_numbers: table
```

## Table Format Benefits

The table format:
- ✅ Works natively on GitHub (no CSS required)
- ✅ Line numbers are visually separated from code
- ✅ Each line is in its own table row
- ✅ Code is formatted with inline backticks
- ❌ Cannot be copied as continuous code (table structure remains)
