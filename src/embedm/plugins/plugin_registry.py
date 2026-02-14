from importlib.metadata import entry_points

from .plugin_base import PluginBase


class PluginRegistry:
    def __init__(self) -> None:
        # Initialize the actual dictionary here
        self.lookup: dict[str, PluginBase] = {}

    @property
    def count(self) -> int:
        return len(self.lookup)

    def load_plugins(self, enabled_plugins: set[str] | None = None, verbose: bool = False) -> None:
        plugins = entry_points(group='embedm.plugins')

        if verbose:
            print(f"discovered {len(plugins)} plugins.")

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
