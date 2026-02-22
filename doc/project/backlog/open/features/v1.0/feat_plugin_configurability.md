FEATURE: Plugin configurability
========================================
Draft  
Release v1.0
Created: 20/02/2026  
Closed: `<date>`  

## Description

We have a configuration to control the main process but we don't have a way to configure the plugins. 

## Points of discussion

**Why do we need this?** 

Config controls all embedms configurable behavior for all plugins in an operation. This way the user doesn't have to repeat the same settings for every plugin.

## Example

```yaml
...

# plugin load order
plugin_sequence:
  - embedm_plugins.file_plugin
  - embedm_plugins.hello_world_plugin
  - embedm_plugins.toc_plugin
  - embedm_plugins.table_plugin

plugin_configuration (move to its own config file?):
    - name: embedm_plugins.file_plugin
        - region_start: "embedm.start:{tag}"
        - region_end: "embedm.end:{tag}"
    - name: embedm_plugins.toc_plugin
        - prefix: "-"
        - indent: "   "

```
## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`