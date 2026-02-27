FEATURE: Parsed data cache for table plugin
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: Claude

## Description

When multiple table directives in a single document reference the same source file (e.g. a large
CSV), `validate_input` currently parses the file into rows once per directive node. The raw file
content is cached by `FileCache`, but the parsed representation (`list[Row]`) is not shared,
so parse cost scales linearly with the number of directives.

A parsed-data cache keyed on the resolved source path would allow the second and subsequent
directives referencing the same file to skip CSV/TSV/JSON parsing entirely and receive the
pre-parsed rows directly.

Related: `feat_add_time_to_verbose` — timing instrumentation will confirm the magnitude of
this cost before committing to the implementation.

## Acceptance criteria

DISCUSS

## Comments

22/02/26 FS: Identified while profiling manual/src/table_plugin.md — 10 table directives all
reading business-financial-data-september-2025-quarter.csv (9,075 rows). FileCache avoids the
disk read but parse cost (csv.DictReader over io.StringIO) still runs 10 times. Defer until
timing data confirms this is worth the added complexity.
