from types import SimpleNamespace

str_resources = SimpleNamespace(
    err_plugin_load_failed="failed to load plugin '{name}': {exc}",
    err_plugin_missing_attributes="plugin '{name}' is missing required attribute(s): {attrs}",
    err_duplicate_directive_type="plugin '{name}' claims directive_type '{dtype}' already registered by '{existing}'",
)
