FEATURE: CLI Dry run
========================================
Draft
Release v1.0
Created: 20/02/26
Closed: `<date>`
Created by: FS / Claude

## Description

Add a `--dry-run` CLI flag that compiles documents fully but does not write any output
files. The compiled result is printed to stdout instead. Allows the user to preview what
would be written without touching the filesystem — useful during authoring and debugging.

`--dry-run` is most meaningful when `--output-file` or `--output-directory` is set;
without those flags the default behaviour already writes to stdout, so `--dry-run` has
no effect.

### Implementation note

The `is_dry_run` field already exists on `Configuration` and `orchestration.py` already
respects it in `_write_output()` and `_write_directory_output()`. The remaining work is
wiring up the CLI flag in `cli.py`.

## Acceptance criteria

1. `--dry-run` (short form `-n`) is accepted as a CLI flag.
2. When `--dry-run` is set, compilation runs in full (planning + transformation).
3. No files are written regardless of `--output-file` or `--output-directory`.
4. The compiled result is printed to stdout.
5. `--dry-run` is mutually exclusive with `--verify`.
6. `--verbose` output works normally alongside `--dry-run`.

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
