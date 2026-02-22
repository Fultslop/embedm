FEATURE: Add duration per plan node
========================================
Draft
Release v1.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS/Claude

## Description

When `-v / --verbose` is active, capture and print duration whenever:

- the file cache loads a file from disk (cache miss)
- each plugin method is called: `validate_directive`, `validate_input`, `transform`

Duration is measured in milliseconds and printed as seconds with three decimal places (e.g. `0.043s`).
All timing output is written to **stderr**.

The total wall-clock duration from process start to completion is always appended to the summary
line, regardless of `-v`.

### Verbose timing line format

```
[cache miss] 0.012s — /path/to/file.csv
[validate_directive] 0.001s — table: /path/to/file.csv
[validate_input] 0.043s — table: /path/to/file.csv
[transform] 0.002s — table: /path/to/file.csv
```

### Summary line format (always)

```
embedm process complete, 3 files written to /path, 13 ok, 0 warnings, 0 errors, completed in 0.312s
```


## Acceptance criteria

### Cache miss timing (verbose only)

- AC1: When `-v` is active and `get_file()` loads a file from disk, a timing line is written to
  stderr containing: the label `cache miss`, the file path, and the load duration in `X.XXXs` format.
- AC2: Cache hits produce no timing output.
- AC3: When `-v` is not active, no cache timing lines are emitted and no timing measurement is made
  for cache events.

### Plugin method timing (verbose only)

- AC4: When `-v` is active, after each call to `validate_directive`, `validate_input`, and
  `transform`, a timing line is written to stderr containing: the method name, the directive type,
  the source path, and the duration in `X.XXXs` format.
- AC5: All three plugin methods are timed: `validate_directive`, `validate_input`, and `transform`.
- AC6: When `-v` is not active, no plugin method timing lines are emitted and no timing measurement
  is made for plugin calls.

### Duration format

- AC7: All durations are measured using a monotonic clock (`time.perf_counter`).
- AC8: All durations are formatted as seconds with exactly 3 decimal places (e.g. `0.043s`,
  `1.203s`).

### Summary total (always)

- AC9: The summary line always includes the total wall-clock duration from process start to summary
  print, regardless of the `-v` flag. Format: `completed in X.XXXs` appended to the existing
  summary.
- AC10: The individual verbose timing lines (cache + plugin) allow the user to sum per-node costs
  and compare against the total to identify orchestration overhead.


## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
