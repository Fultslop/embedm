We're going to add a table plugin. This plugin takes as source a csv or tsv file, json and creates a markdown table. If you need a reference you can look at the ./archive/src/embedm_plugins/table_plugin. 

Keep in mind we need to support an sql-light feature set as we discussed before:

Safe to add — well-defined parsing, no ambiguity:

limit / offset: trivial list slicing, no parsing
select: split on commas, handle col as alias with a single regex — clear input format, clear failure mode
order_by: split on commas, split each part by space to get (column, asc|desc) — same story
Where I'd be cautious — the where string:

The risk isn't the initial implementation, it's the contract. The moment you accept a free-form string, users will write whatever they'd write in SQL and expect it to work. You'll get bug reports for:

OR logic
LIKE/IN/BETWEEN
type coercion edge cases ("24" vs 24)
parentheses / operator precedence
escaped quotes in string values
There's no natural stopping point once you've accepted a string parser.

What I'd suggest instead — structured filtering:


type: table
source: some_file.csv
select: "column_x, column_y as y"
order_by: "y desc"
limit: 10
offset: 20
filter:
  column_x: "value"    # exact match
  y: "<= 24"           # operator + literal
A filter mapping where each value is either a bare literal (exact match) or "op literal" where op is one of =, !=, <, <=, >, >=. Multiple keys are implicitly ANDed.

This gives you explicit scope: you support exactly these operators, one condition per column, no OR, no nesting. Users who need something more complex can pre-filter their CSV. The failure mode is also clean — an unrecognised operator string returns an error Status rather than silently misfiltering.

On IS NULL: I'd skip it for now or handle it as a special string "is null" / "is not null" if it comes up. Most table sources from real CSVs represent nulls inconsistently anyway.

The short version: select, limit, offset, order_by — yes. where as a string — replace with a structured filter map with a fixed operator vocabulary. That gives familiar semantics, a hard scope boundary, and no parser to maintain.

So the full options surface ends up being:


select: "col_a, col_b as b"
order_by: "b desc"
limit: 10
offset: 0
date_format: "%Y-%m-%d"    # applied to date/datetime values
null_string: "-"            # what to render for nulls
max_cell_length: 80         # truncates anything longer
Anything that doesn't fit renders as a truncated string. The user excludes columns they can't handle via select. That's a complete, bounded contract with no gnarly type-specific code paths.

Write a transformer, plugin and tests that provide this functionality. Ask if anything is not clear or if you have suggestions to improve / alter this feature.