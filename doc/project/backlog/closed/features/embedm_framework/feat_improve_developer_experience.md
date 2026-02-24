FEATURE: `Improve Plugin Developer Experience`
========================================
Draft
Planned release: v1.0
Created: 24/02/26
Closed: ``
Created by: Claude

## Description

Writing a minimal plugin currently requires 10–12 imports, a 5-parameter `transform` signature,
and boilerplate `validate_directive` copy-paste. The goal is to reduce a working plugin to
a single import and a clean method signature, lowering the barrier for external plugin authors.

Three changes achieve this:

1. **`embedm.plugins.api` re-export module** — a single import surface for plugin authors
   covering all commonly needed types (`PluginBase`, `Status`, `StatusLevel`, `Directive`,
   `Fragment`, `PlanNode`, `PluginConfiguration`, `PluginContext`, `ValidationResult`).

2. **`PluginContext` dataclass** — bundles `file_cache`, `plugin_registry`, and `plugin_config`
   into one object. The `transform` signature drops from 5 parameters to 3:
   `transform(self, plan_node, parent_document, context=None)`.
   Constructor injection is not used (plugins are singletons loaded before any compile context
   exists); `PluginContext` achieves the same DX goal without registry changes.

3. **`validate_directive` non-abstract with default `return []`** — the type-mismatch guard
   every plugin currently copies is redundant (the registry already routes by directive type).
   Plugins only override `validate_directive` when they have real validation to add.

Resulting minimal plugin:

```python
from embedm.plugins.api import PluginBase

class MyPlugin(PluginBase):
    name = "my plugin"
    api_version = 1
    directive_type = "my-type"

    def transform(self, plan_node, parent_document, context=None):
        return "output"
```

## Acceptance criteria

- `embedm.plugins.api` exists and exports: `PluginBase`, `Directive`, `Fragment`, `PlanNode`,
  `Status`, `StatusLevel`, `PluginConfiguration`, `PluginContext`, `ValidationResult`
- `PluginContext` dataclass exists in `embedm.plugins.plugin_context` with fields:
  `file_cache: FileCache`, `plugin_registry: PluginRegistry`, `plugin_config: PluginConfiguration | None`
- `PluginBase.transform` signature is `(self, plan_node, parent_document, context: PluginContext | None = None) -> str`
- `PluginBase.validate_directive` is non-abstract and returns `[]` by default
- `hello_world_plugin.py` uses only `from embedm.plugins.api import PluginBase` for its embedm imports
  and has no `validate_directive` override
- All 6 bundled plugins updated to new signature; plugins that use `file_cache` access it via `context.file_cache`
- Both call sites (`orchestration.py`, `file_transformer.py`) build and pass `PluginContext`
- All existing tests pass unchanged
- Import linter contracts remain satisfied

## Comments

`24/02/26 Agent: Designed based on user feedback after building first external plugin (MermaidLightPlugin).
The 5-param transform and mandatory validate_directive boilerplate were the primary friction points.
PluginContext preferred over constructor injection because plugins are registry singletons;
FileCache/PluginRegistry don't exist at plugin load time.`
