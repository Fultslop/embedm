TECHNICAL IMPROVEMENT: Improve the output
=============================================================================
Draft  
Created: 27/02/2026  
Closed: `<date>`  
Created by: FS  

## Description

During execution we only print what file has completed. The user doesn't see the current file that embedm is working on, creating the impression — in case of long operations — the preceding file is causing the delay. This is not a great user experience.

This feature improves the output experience by:

- Showing the currently active file(s) during compilation with live progress (per-node percentage and elapsed time)
- Applying color to output
- Introducing an event-based logging system to support the future multithreading model
- Refining the verbosity model per execution state
- Removing verbosity level 3 (`-v 3`); it will be silently treated as `-v 2` until redefined
- Adding TTY-aware rendering: live ANSI output only when stdout is an interactive terminal; plain line-by-line output otherwise

Note: batch execution (plan-all → compile-all with configurable batch size) is a separate feature. See `tech_batch_execution.md`. The output system defined here is designed to be extended by that feature.

### TTY-aware renderer

Two rendering modes:

- **Interactive renderer**: ANSI escape codes, cursor movement, and color. Active when `sys.stdout.isatty()` is `True` and color is not suppressed.
- **Stream renderer**: Plain text, line-by-line, no control codes. Active when stdout is redirected (pipe, file, CI).

The event system dispatches to the appropriate renderer automatically. Switching between renderers requires no changes to the orchestrator.

### Color

Color is applied in interactive mode. Color is suppressed when any of the following are true:

- The `NO_COLOR` environment variable is set (any value), per https://no-color.org/
- The `--no-color` CLI flag is passed
- `sys.stdout.isatty()` is `False` (stream renderer active)

Proposed color scheme:

| Element | Color |
|---|---|
| `[OK]` | Green |
| `[ERR]` | Red |
| Planning and runtime warnings | Yellow |
| Active file progress | Cyan |
| Title line (`Embedm [N/M]`) | Bold |
| Config / input / output labels | Dim |

### Non-interactive error prompts

States that require user input ("ask the user if they want to continue") behave as follows:

- **Interactive (TTY)**: prompt the user with `y/N/a/x` per the current way of working (enter = N).
- **Non-interactive (no TTY)**: assume `X`, fail the pipeline, and exit with a non-zero exit code.

### Exception detail

When a file fails at runtime, the completion line shows the exception message only — not the full Python traceback. This keeps output readable at default verbosity.

### Event system

The output renderer subscribes to the event dispatcher defined in `tech_event_system.md`. See that document for the full event catalog, dispatcher interface, and producer integration details.

The renderer registers handlers for each relevant event type and maintains its own display state. Verbosity filtering is the renderer's responsibility — it receives all events and decides what to act on.

### States

Execution phases during a single run:

1. Start
2. Init / plugin verification
3. Plan
4. Compilation
5. Complete

---

### The start state

**Verbosity 0 — silent**

Nothing shown.

**Verbosity 1 — minimal**

```shell
Embedm v1.1
```

**Verbosity 2 — default**

```shell
Embedm v1.1
Config: DEFAULT | config/file/relative/path
Input:  stdin | file | directory
Output: stdout | file | directory
```

---

### The init / plugin verification state

**Verbosity 0 — silent**

Nothing shown.

**Verbosity 1 — minimal**

Nothing shown on success. On error:

```shell
[ERR] <plugin error description>
```

**Verbosity 2 — default**

On success:

```shell
X plugins discovered, Y plugins loaded.
```

On error (same as v1):

```shell
[ERR] <plugin error description>
```

---

### The plan state

**Verbosity 0 — silent**

Nothing shown on success. On error, ask to continue (non-TTY: fail and exit).

**Verbosity 1 — minimal**

Nothing shown on success. On error, ask to continue (non-TTY: fail and exit).

**Verbosity 2 — default**

Files are shown as they are planned:

```shell
Planning X file(s)
  [1/X] rel_path/filename_a.md
  [2/X] rel_path/filename_b.md
  ...
```

On planning error for a file:

```shell
  [2/X] rel_path/filename_b.md
  [ERR] <planning error message>
  Continue? [Y/N]
```

---

### The compilation state

**Verbosity 0 — silent**

Nothing shown on success. On error, ask to continue (non-TTY: fail and exit).

**Verbosity 1 — minimal**

Nothing shown on success. On error, ask to continue (non-TTY: fail and exit).

**Verbosity 2 — default**

The display has two sections:

- A **completion list** that grows as files finish (printed permanently above the live section)
- A **live progress section** that overwrites in place on each update (interactive renderer only)

Format:

```
<COMPLETION LIST>
    <STATE> <TIME>  <COMPLETED FILE> -> <OUTPUT_PATH>

<TITLE> <OVERALL PROGRESS> <ELAPSED>
 - <ACTIVE FILE 1>: <FILE_PROGRESS> (<TIME>)
 - <ACTIVE FILE 2>: <FILE_PROGRESS> (<TIME>)
 - ...
```

`FILE_PROGRESS` is a two-digit percentage based on the number of nodes compiled for that file.

In the interactive renderer, the live section overwrites from the `Embedm [N/M]` line downward on each update. In the stream renderer, the live section is omitted and only completion events are printed as they occur.

**Example steps (single-threaded, 3 files):**

Step 1:
```shell
Embedm [0/3] 0.00s
 - rel_path/filename_a.md: 0% (0.00s)
```

Step 2:
```shell
Embedm [0/3] 0.10s
 - rel_path/filename_a.md: 83% (0.10s)
```

Step 3 — filename_a completes:
```shell
[OK] 1.22s  rel_path/filename_a.md -> rel_output_path/filename_a.md

Embedm [1/3] 1.22s
 - rel_path/filename_b.md: 15% (0.00s)
```

Step 4 — filename_b errors:
```shell
[OK] 1.22s  rel_path/filename_a.md -> rel_output_path/filename_a.md
[ERR] 2.23s rel_path/filename_b.md
  <exception message>

Embedm [2/3] 3.45s
 - rel_path/filename_c.md: 55% (1.00s)
```

Step 5 — filename_c completes, run finished (live section collapses):
```shell
[OK] 1.22s  rel_path/filename_a.md -> rel_output_path/filename_a.md
[ERR] 2.23s rel_path/filename_b.md
  <exception message>
[OK] 1.01s  rel_path/filename_c.md -> rel_output_path/filename_c.md
```

---

### The complete state

**Verbosity 0 — silent**

Nothing shown. Exit code communicates outcome.

**Verbosity 1 — minimal**

On success:
```shell
Embedm complete, 3 files ok, total time: 3.4s
```

On error:
```shell
Embedm complete, 2 files ok, 1 error, total time: 3.4s
```

**Verbosity 2 — default**

On success (same as v1):
```shell
Embedm complete, 3 files ok, total time: 3.4s
```

On error, re-list errors above the summary (they may have scrolled out of view during compilation):
```shell
[ERR] 2.23s rel_path/filename_b.md
  <exception message>

Embedm complete, 2 files ok, 1 error, total time: 3.4s
```

## Acceptance criteria

`<Optional: list of line description of tests to measure improvements>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
