from .plugin_base import PluginBase


class PluginRegistry:
    lookup: dict[str, PluginBase]

    def resolve_plugins(self) -> None:
        raise NotImplementedError("todo")

    def find_plugin(self, name: str) -> PluginBase:
        raise NotImplementedError("todo")
