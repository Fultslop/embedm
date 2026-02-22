FEATURE: CLI Verify option
========================================
Draft
Release v1.0
Created: 20/02/2026
Closed: `<date>`
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
- **Incremental compilation** (skip unchanged files via a manifest) is a separate performance
  optimisation deferred to v2.0.

## Acceptance criteria

1. `--verify` is accepted as a CLI flag; it is mutually exclusive with `--dry-run` and
   requires `--output-file` or `--output-directory` (missing target yields an error and
   exit code 1).
2. When `--verify` is set, compilation runs in full but no files are written.
3. For each compiled document, the result is compared byte-for-byte against the existing
   output file.
4. If an output file does not exist, it is treated as stale.
5. If all output files are up to date, the process exits with code 0.
6. If any output file is stale or missing, the stale paths are reported to stderr and the
   process exits with code 1.
7. The compare result (up-to-date / stale / missing) is always reported to stderr for
   each checked file, regardless of `--verbose`. `--verbose` may add further detail
   (timing, plugin discovery, etc.) as in normal mode.
8. Compilation errors (parse failures, plugin errors) are still reported as errors and
   exit code 1 regardless of `--verify`.

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
