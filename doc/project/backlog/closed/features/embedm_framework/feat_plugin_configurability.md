FEATURE: Plugin configurability
========================================
Release v1.0  
Created: 20/02/2026  
Closed: 22/02/2026  
Created by: FS/Claude

## Description

We have a configuration to control the main process but we don't have a way to configure the plugins.

Config controls all embedm's configurable behaviour for all plugins in an operation. This way the
user doesn't have to repeat the same settings for every directive. It also allows exposing properties
that belong in configuration rather than per-directive options (e.g. region marker format).

## Design

**Config location:** `plugin_configuration` section inside `embedm-config.yaml`. No separate file.

**YAML schema:**
```yaml
plugin_configuration:
  embedm_plugins.file_plugin:
    region_start: "region:{tag}"
    region_end: "endregion:{tag}"
  embedm_plugins.toc_plugin:
    prefix: "-"
    indent: "   "
```

**Two-phase validation after config + plugins are loaded:**

1. **Structural (framework)** — `PluginBase.get_plugin_config_schema() -> dict[str, type] | None`
   The plugin returns the keys it accepts and their expected types, or `None` if it accepts no config.
   The framework iterates loaded plugins, validates each plugin's config section against its schema:
   - Wrong type → ERROR
   - Unknown key → silently ignored; logged to stderr when `--verbose` is set
   - Missing key → not an error; plugin uses its hardcoded default

2. **Semantic (plugin)** — `PluginBase.validate_plugin_config(settings: dict[str, Any]) -> list[Status]`
   No-op default on `PluginBase`. Overridden by plugins that have rules beyond type correctness
   (e.g. `file_plugin` requires `{tag}` to be present in `region_start` / `region_end` so that
   region names can be interpolated at extraction time).

**Runtime access:** validated per-plugin settings are stored in `PluginConfiguration` as
`plugin_settings: dict[str, dict[str, Any]]`, keyed by module name. Each plugin reads its own
key from `plugin_config.plugin_settings.get(self.__class__.__module__, {})`.

## Acceptance criteria

* `plugin_configuration` is an optional section in `embedm-config.yaml`. Omitting it entirely is
  valid and produces no errors.

* A plugin with `get_plugin_config_schema()` returning `{"region_start": str, "region_end": str}`
  accepts a valid string value for both keys without errors.

* A value with the wrong type (e.g. `region_start: 42`) produces an ERROR status at startup.

* An unknown key in a plugin's config section is silently ignored at runtime, and logged to stderr
  when `--verbose` is active.

* A plugin that returns `None` from `get_plugin_config_schema()` causes its entire config section
  (if present) to be silently ignored (same unknown-key rule applied uniformly).

* `file_plugin` overrides `get_plugin_config_schema()` returning `{"region_start": str, "region_end": str}`
  and overrides `validate_plugin_config()` to report an ERROR if either value does not contain `{tag}`.

* `file_plugin` uses configured `region_start`/`region_end` values (with `{tag}` substituted for the
  region name) when extracting regions; falls back to `md.start:{tag}` / `md.end:{tag}` if not configured.

* All existing region extraction tests continue to pass without configuration changes.

* New unit tests cover: schema type mismatch error, unknown key ignored, semantic `{tag}` missing error,
  and correct region extraction using a custom marker.

## Comments

**22/02/26 Claude:**

Two-phase approach keeps structural validation (mechanical, framework-level) separate from semantic
validation (meaningful, plugin-level). This mirrors the existing `validate_directive` → `validate_input`
→ `transform` pipeline pattern. Unknown-key silent-ignore keeps plugins forwards-compatible as new
keys are added to future plugin versions; the `--verbose` log ensures discoverability during debugging.
`{tag}` semantic check is necessary: a marker without `{tag}` compiles to a fixed-string regex that
matches every line or no line, silently breaking all region extractions in the project.
