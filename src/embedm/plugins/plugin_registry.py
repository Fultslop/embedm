from importlib.metadata import entry_points

from embedm.domain.status_level import Status, StatusLevel

from .plugin_base import PluginBase
from .plugin_resources import str_resources


class _PluginLookup(dict):  # type: ignore[type-arg]
    """dict subclass that maintains a secondary directive_type → plugin index."""

    def __init__(self) -> None:
        super().__init__()
        self._by_directive_type: dict[str, PluginBase] = {}

    def __setitem__(self, key: str, value: PluginBase) -> None:
        super().__setitem__(key, value)
        self._by_directive_type[value.directive_type] = value

    def __delitem__(self, key: str) -> None:
        plugin = self[key]
        self._by_directive_type.pop(plugin.directive_type, None)
        super().__delitem__(key)


class PluginRegistry:
    def __init__(self) -> None:
        self.lookup: _PluginLookup = _PluginLookup()
        # Populated by load_plugins; each entry is (entry_point_name, module_path).
        self.discovered: list[tuple[str, str]] = []
        self.skipped: list[tuple[str, str]] = []

    @property
    def count(self) -> int:
        return len(self.lookup)

    def load_plugins(self, enabled_modules: set[str] | None = None) -> list[Status]:
        """Load all registered plugins. Returns errors for any that fail to load.

        enabled_modules: set of module paths (e.g. 'embedm_plugins.file_plugin') to load.
        If None, all discovered plugins are loaded.
        """
        plugins = entry_points(group="embedm.plugins")
        errors: list[Status] = []
        self.discovered = []
        self.skipped = []

        for entry in plugins:
            module_path = entry.value.split(":")[0]
            self.discovered.append((entry.name, module_path))

            if enabled_modules is not None and module_path not in enabled_modules:
                self.skipped.append((entry.name, module_path))
                continue

            try:
                plugin_class = entry.load()
                instance = plugin_class()
            except Exception as exc:
                errors.append(
                    Status(StatusLevel.ERROR, str_resources.err_plugin_load_failed.format(name=entry.name, exc=exc))
                )
                continue

            self.lookup[instance.name] = instance

        return errors

    def get_plugin(self, name: str) -> PluginBase | None:
        return self.lookup.get(name)

    def find_plugin_by_directive_type(self, directive_type: str) -> PluginBase | None:
        """Find a plugin that handles the given directive type."""
        return self.lookup._by_directive_type.get(directive_type)
