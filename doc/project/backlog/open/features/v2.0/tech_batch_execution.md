TECHNICAL IMPROVEMENT: Batch execution model
=============================================================================
Draft
Created: 27/02/2026
Closed: `<date>`
Created by: FS

## Description

Currently embedm processes files one at a time: plan one file, compile it, repeat. This feature changes the execution model to plan all files first, then compile all, with a configurable batch size cap to handle large file sets efficiently.

This is a prerequisite for the planned multithreading model and enables more accurate overall progress reporting (all file counts are known before compilation begins).

### Execution model

**Single pass (file count <= batch_size):**

1. Start
2. Init / plugin verification
3. Plan all N files
4. Compile all N files
5. Complete

**Batched (file count > batch_size):**

1. Start
2. Init / plugin verification
3. For each batch B of up to `batch_size` files:
   - Plan batch files
   - Compile batch files
4. Complete

### Configuration

A `batch_size` key is added to the config.

- Default: `32`
- Must be a positive integer. `0` or any negative value is a config validation error (handled by existing config verification).
- Not overridable from the CLI.

### Output

The output system defined in `tech_improve_output.md` is extended to include batch context when more than one batch is needed. When only a single batch is used (file count <= `batch_size`), output is identical to the single-pass format — no batch indicators are shown.

**Plan state (verbosity 2) — batched:**

```shell
Planning X file(s), Y batch(es)
Batch [1/Y]:
  [1/X] rel_path/filename_a.md
  [2/X] rel_path/filename_b.md
```

**Compilation state title line (verbosity 2) — batched:**

```shell
Embedm [0/X] Batch [1/Y] 0.00s
 - rel_path/filename_a.md: 0% (0.00s)
```

All other output format rules from `tech_improve_output.md` apply unchanged.

## Acceptance criteria

`<Optional: list of line description of tests to measure improvements>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
