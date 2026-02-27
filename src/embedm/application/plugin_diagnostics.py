from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.plugin_registry import PluginRegistry

from .application_resources import str_resources as app_resources
from .configuration import Configuration


class PluginDiagnostics:
    """Post-load cross-check of registry state against configuration."""

    def check(self, registry: PluginRegistry, config: Configuration) -> list[Status]:
        """Return warnings for plugin_sequence entries with no matching entry point."""
        discovered_modules = {m for (_, m) in registry.discovered}
        return [
            Status(
                StatusLevel.WARNING,
                app_resources.warn_unresolved_plugin_sequence.format(module=module),
            )
            for module in config.plugin_sequence
            if module not in discovered_modules
        ]
