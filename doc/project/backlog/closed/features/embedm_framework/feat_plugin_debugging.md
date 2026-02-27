FEATURE: Plugin debugging 
========================================
Draft
Release v1.1
Created: 27/02/2026
Closed: `<date>`
Created by: FS

## Description

When creating new plugins there are various things that can go wrong. 

* The user forgets to install their local plugins (via `pip install`)
* The user might forget to register their plugins in their pyproject 
* The user might forget to implement add pyproject 
* The user might forget to register their plugins under a wrong name or package name
* The user might forget to register in the embedm-config 
* The user might make errors by forgetting to add 'name' and 'directive_type' to their plugins.
* The user might forget to derive their plugin from the pluginbase.
* (other things that can go wrong)

The user should have a command line option -p / --plug_in_list which lists which plugins are loaded and 'enabled' (ie part of the plugin sequence) as well as do a sanity check to verify as much as the possible issues listed above and report back to the user.

We should also consider moving this validation / verification into its own service as to not overload orchestration or the plugin registry. This validation should be called from the orchestation. 

## Acceptance criteria

### `-p` / `--plugin-list` flag
- Works without an input file (config only); exits after printing, no compilation
- Prints a formatted list of all loaded plugins (name, directive_type, module)
- Prints all `plugin_sequence` entries that have no matching entry point (not installed / not registered) as warnings
- Prints all discovered-but-skipped plugins (registered entry point not in `plugin_sequence`) as informational
- Reports plugins that do not inherit from `PluginBase` as errors
- Reports plugins with missing required attributes (`name`, `directive_type`) as errors (these are already caught at load time — `-p` surfaces them explicitly)
- Reports duplicate `directive_type` conflicts (two loaded plugins claiming the same type) as errors
- Exit code 0 if no errors, 1 if any errors found

### During normal compilation (warning mode)
- A `plugin_sequence` entry with no matching entry point emits a WARNING at default verbosity, before compilation begins
- Discovered-but-skipped plugins are informational only (no change to existing silent behaviour)
- Warnings do not block compilation

### Architecture
- Validation logic lives in a dedicated `PluginDiagnostics` service (separate from `PluginRegistry` and `orchestration`)
- `PluginDiagnostics` takes `(registry, config)` and returns a list of `Status` objects
- Called from orchestration for both `-p` mode and normal startup warning

## Comments

`27/02/26 FS/Agent: folds in tech_warn_on_unresolved_plugin_sequence_entry. Unresolved plugin_sequence entries → WARNING during normal runs, clearly flagged in -p output. Not-installed is not distinguishable from not-registered — both surface as "no matching entry point".`