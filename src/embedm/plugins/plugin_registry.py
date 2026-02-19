from importlib.metadata import entry_points

from .plugin_base import PluginBase
from .plugin_resources import str_resources


class PluginRegistry:
    def __init__(self) -> None:
        # Initialize the actual dictionary here
        self.lookup: dict[str, PluginBase] = {}

    @property
    def count(self) -> int:
        return len(self.lookup)

    def load_plugins(self, enabled_plugins: set[str] | None = None, verbose: bool = False) -> None:
        plugins = entry_points(group="embedm.plugins")

        if verbose:
            print(str_resources.registry_show_len_plugins.format(len_plugins=len(plugins)))

        # load the plugins
        for entry in plugins:
            # todo: catch failure to load plugin
            plugin_class = entry.load()
            instance = plugin_class()

            if enabled_plugins is None or instance.name in enabled_plugins:
                if verbose:
                    print(f"    adding plugin '{instance.name}'.")
                self.lookup[instance.name] = instance
            elif verbose:
                print(f"    rejected plugin '{instance.name}'.")

    def get_plugin(self, name: str) -> PluginBase | None:
        return self.lookup.get(name)

    def find_plugin_by_directive_type(self, directive_type: str) -> PluginBase | None:
        """Find a plugin that handles the given directive type."""
        for plugin in self.lookup.values():
            if plugin.directive_type == directive_type:
                return plugin
        return None
