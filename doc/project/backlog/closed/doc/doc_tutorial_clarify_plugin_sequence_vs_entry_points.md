TECHNICAL IMPROVEMENT: `Tutorial does not explain the relationship between plugin_sequence and entry points`
========================================
Created: `27/02/26`
Closed: `27/02/26`
Created by: `Agent (plugin-validator skill)`

## Description

The plugin tutorial (`.doc\manual\src\assets\tutorial\plugin_tutorial.md`) presents two separate registration steps — adding the plugin to
`plugin_sequence` in `embedm-config.yaml` and registering an entry point in `pyproject.toml`
— without explaining what each does or why both are required.

The current mental model a reader is likely to form: "one of these registers the plugin,
the other does something else." The actual model: entry points drive discovery (the plugin
must be discoverable); `plugin_sequence` controls load order. Without this explanation,
users who encounter a load failure have no conceptual frame for debugging it.

## Acceptance criteria

- Tutorial includes a brief explanation (1–3 sentences) of what each registration step
  does: entry points = discovery, plugin_sequence = load order
- Tutorial includes a short explanation how this ties in with the '-p' cli option.
- The explanation appears before or alongside the two registration steps

## Comments

`27/02/26 Agent: discovered during plugin-validator skill run — both steps followed correctly but the lack of explanation made silent failures harder to interpret`
