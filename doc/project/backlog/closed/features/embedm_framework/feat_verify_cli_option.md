FEATURE: CLI Verify option
========================================
Draft  
Release v1.0  
Created: 20/02/2026  
Closed: 23/02/2026 
Created by: ChatGpt / FS / Claude  

## Description

Add a `--verify` CLI option that compiles documents and compares the result against
existing output files without writing anything. Exits with a non-zero exit code if any
output is stale (i.e. the compiled result differs from the file on disk). Enables CI
pipelines to catch outdated compiled docs.

`--verify` requires `--output-file` or `--output-directory` — there is nothing to compare
against when writing to stdout.

### Design notes

- **Compile, compare, do not write.** Full compilation runs internally (same code path as
  a normal run). The compiled result is compared byte-for-byte against the existing output
  file. No manifest or timestamp tracking is needed; byte comparison is always correct and
  works reliably in CI environments where file timestamps cannot be trusted.
- **Exit code on compilation errors.** Any compilation error (parse failure, plugin error,
  invalid directive) causes exit code 1. This applies in both normal mode and `--verify`
  mode. Previously `main()` only exited non-zero for CLI argument and config-load errors;
  this is corrected as part of this feature.
- **Line endings.** A `line_endings` option in `embedm-config.yaml` (`lf` | `crlf`,
  default `lf`) controls the line ending applied to output files before writing. In
  `--verify` mode, the compiled result is normalised using this option before the
  byte-for-byte comparison, so the comparison reflects exactly what embedm would write.
  Project-level config (not per-directive) is the right scope: line endings are a
  per-repo concern and keeping them consistent across all output files avoids CI
  non-reproducibility on Windows vs Linux runners.
- **Verify-mode summary.** The summary line in `--verify` mode reports
  `files checked / up-to-date / stale` instead of `files written`.
- **Incremental compilation** (skip unchanged files via a manifest) is a separate performance
  optimisation deferred to v2.0.

## Acceptance criteria

1. `--verify` is accepted as a CLI flag; it is mutually exclusive with `--dry-run` and
   requires `--output-file` or `--output-directory` (missing target yields an error and
   exit code 1).
2. When `--verify` is set, compilation runs in full but no files are written.
3. For each compiled document, the result is normalised with the configured `line_endings`
   option and then compared byte-for-byte against the existing output file.
4. If an output file does not exist, it is treated as stale.
5. If all output files are up to date and there are no compilation errors, the process
   exits with code 0.
6. If any output file is stale or missing, the stale paths are reported to stderr and the
   process exits with code 1.
7. The compare result (up-to-date / stale / missing) is always reported to stderr for
   each checked file, regardless of `--verbose`. `--verbose` may add further detail
   (timing, plugin discovery, etc.) as in normal mode. The final summary line reports
   `N files checked, N up-to-date, N stale` instead of `N files written`.
8. Compilation errors (parse failures, plugin errors) cause exit code 1 in all modes
   (normal and `--verify`). This corrects the prior behaviour where only CLI argument
   and config-load errors triggered a non-zero exit.
9. A `line_endings` field in `embedm-config.yaml` accepts `lf` (default) or `crlf`.
   When set, all output files are written with the specified line ending. In `--verify`
   mode the compiled result is normalised accordingly before comparison. The
   `--verbose` configuration block prints the active `line_endings` value.

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
