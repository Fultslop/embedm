FEATURE: Add "verbose" CLI Option
========================================
Draft
Release: v1.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

We want users to be able to diagnose any problems during planning/execution. As part of this process
the CLI should offer a "verbose" flag (-v / --verbose) which outputs additional diagnostic information
to stderr.

## Acceptance criteria

**Output destination**
All verbose output is written to stderr. This keeps stdout clean for any piped content and follows
the Unix convention for diagnostic output. The planning result (errors/warnings) follows the same
rule: written to stderr when verbose is on.

**Expected output**
The following information is written to stderr when the verbose flag is active:

* Embedm title + version
* Current working directory — determines where source files are read from and output files are
  written to; helps debug path-related errors
* Full merged configuration (all fields)
* Plugin discovery:
    * Entry points discovered (what is registered with the environment after `pip install -e .`)
    * Plugin sequence from config (the ordered module list from `plugin_sequence`)
    * Plugins actually loaded (filtered intersection of the above two), showing for each:
        * Module path
        * Plugin name
        * Directive type it handles
    * Any entry points skipped (discovered but not in `plugin_sequence`)
* Planning tree — one node per source file processed; each node shows:
    * Source file path
    * Status (ok / warning / error)
    * Child nodes for each embedded directive, each showing:
        * Directive type
        * Source path (if any)
        * Status
        * Recursion into embedded source files continues the tree structure
    * When a directive type is not found in the registry, list the registered directive types
      alongside the error so the user can compare
* File cache events: for every cache request, print the full path and whether it was a hit, miss,
  or eviction
* Full path of each output file written
* Short summary (e.g. `embedm process complete, 11 files written to ..., 8 ok, 2 warnings, 1 error`)

**Colors**
Color output is planned for a future iteration. When implemented, colors will follow the `NO_COLOR`
environment variable convention (https://no-color.org): if `NO_COLOR` is set, no color escape codes
are emitted. The current implementation produces plain text only.

**Non-verbose hint**
If the user does not pass -v / --verbose and errors are present, append a hint to the summary:

`embedm process complete, 11 files written to ..., 8 ok, 2 warnings, 1 error. Use -v or --verbose for more information.`

**Unit tests**
* Unit tests capture the expected output for each verbose section
* Unit tests verify the non-verbose hint is appended when errors are present

## Comments

`22/02/2026 FS: Initial draft`
`22/02/2026 FS/Claude: Revised — verbose output to stderr; plugins loaded section expanded to show
entry points vs loaded distinction and directive types; planning tree nodes defined (source path +
status); lookup failures show available directive types; NO_COLOR support noted for future color
implementation; configuration shows all fields.`
