from importlib.metadata import entry_points

from embedm.domain.status_level import Status, StatusLevel

from .plugin_base import PluginBase
from .plugin_resources import str_resources


class PluginRegistry:
    def __init__(self) -> None:
        # Initialize the actual dictionary here
        self.lookup: dict[str, PluginBase] = {}

    @property
    def count(self) -> int:
        return len(self.lookup)

    def load_plugins(self, enabled_modules: set[str] | None = None, verbose: bool = False) -> list[Status]:
        """Load all registered plugins. Returns errors for any that fail to load.

        enabled_modules: set of module paths (e.g. 'embedm_plugins.file_plugin') to load.
        If None, all discovered plugins are loaded.
        """
        plugins = entry_points(group="embedm.plugins")
        errors: list[Status] = []

        if verbose:
            print(str_resources.registry_show_len_plugins.format(len_plugins=len(plugins)))

        for entry in plugins:
            if enabled_modules is not None and entry.value.split(":")[0] not in enabled_modules:
                if verbose:
                    print(f"    skipping plugin '{entry.name}'.")
                continue

            try:
                plugin_class = entry.load()
                instance = plugin_class()
            except Exception as exc:
                errors.append(
                    Status(StatusLevel.ERROR, str_resources.err_plugin_load_failed.format(name=entry.name, exc=exc))
                )
                continue

            if verbose:
                print(f"    adding plugin '{instance.name}'.")
            self.lookup[instance.name] = instance

        return errors

    def get_plugin(self, name: str) -> PluginBase | None:
        return self.lookup.get(name)

    def find_plugin_by_directive_type(self, directive_type: str) -> PluginBase | None:
        """Find a plugin that handles the given directive type."""
        for plugin in self.lookup.values():
            if plugin.directive_type == directive_type:
                return plugin
        return None
