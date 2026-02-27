TECHNICAL IMPROVEMENT: `No warning when a plugin_sequence module has no matching entry point`
========================================
Created: `27/02/26`
Closed: `<date>`
Created by: `Agent (plugin-validator skill)`

## Description

When a module listed in `plugin_sequence` has no registered entry point in the current
Python environment, embedm silently skips it. Even at verbosity level 3, the output only
reports the aggregate counts ("discovered: N entry points", "loaded: N") with no
indication of which module was skipped or why.

This makes the failure mode difficult to diagnose without prior knowledge of the
entry-point discovery mechanism. A warning identifying the unresolved module would make
the root cause immediately apparent.

## Acceptance criteria

- When a `plugin_sequence` entry has no matching entry point, embedm emits a warning
  (visible at default verbosity) identifying the module name that could not be resolved
- The warning is shown before compilation begins, not after

## Comments

`27/02/26 Agent: discovered during plugin-validator skill run — mermaid_plugin listed in plugin_sequence but silently absent from loaded plugins; required -v 3 + prior knowledge to diagnose`
