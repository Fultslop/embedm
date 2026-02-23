FEATURE: Improve user interface
========================================
Draft
Release v1.0
Created: 23/03/2026
Closed: `<date>`
Created by: FS

## Description

The current output on the console is functional but isn't great. To improve it we want to:

* Define a level for the verbose flag with '2' being the default
* The output to be easily readable
* The output to be understandable at a glance
* The output to be nice to look at, for as far as that's possible with console output
* The output to be easily parsable by tools

## Design Decisions

**No logging module**: the output model is already well-separated in `console.py`. Adding the
`logging` module would introduce unnecessary configuration surface without meaningful benefit.
Verbosity levels are implemented as a CLI-driven integer gate, gated in `orchestration.py`.

**Error suppression with accept-all**: When `--accept-all` is set, embedm proceeds through all
errors without prompting. In that case, error messages are suppressed at levels 0 and 1 — the
summary still shows the error count. Without `--accept-all`, the user must decide, so errors
and the prompt always appear regardless of level.

**Tool-parsable vs human-readable**: Both goals are served by keeping human-readable prose on
`stderr` and relying on the exit code for machine parsing. No structured key=value output is added.

**ASCII status indicators**: Output uses `[OK]`, `[WARN]`, `[ERROR]` for tool safety.
ANSI colour support is out of scope for this implementation.

## Acceptance criteria

* `-v N` / `--verbose N` sets the verbosity level (0–3). `-v` alone (no number) is equivalent
  to `-v 3`. An invalid level (outside 0–3) is a CLI error.

  - **0: silent** — assumed for CI/CD pipelines that read the exit code
    - No output to the console
    - If `--accept-all` is NOT set: user prompt still appears on errors (user must decide)
    - If `--accept-all` IS set: fully silent, including errors

  - **1: minimal**
    - Title
    - Summary line (outcomes including error count)
    - If `--accept-all` is NOT set: error messages and prompt appear on errors
    - If `--accept-all` IS set: no error messages; error count visible in summary

  - **2: default** *(no `-v` flag)*
    - Title
    - In directory mode: one progress line per file as it completes: `  filename.md  [OK]`
    - Error messages always shown (whether or not `--accept-all` is set)
    - Summary line

  - **3: verbose** *(equivalent to the old `--verbose`)*
    - All diagnostic output — configuration dump, plugin list, plan tree, timing

* No functional changes (compile, write, verify behaviour unchanged)

* Update tests where needed

## Comments

23/02/26 Claude: Clarifications recorded above after discussion with FS.
