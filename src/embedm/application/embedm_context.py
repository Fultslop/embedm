from dataclasses import dataclass

from embedm.io.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry

from .configuration import Configuration


@dataclass
class EmbedmContext:
    config: Configuration
    file_cache: FileCache
    plugin_registry: PluginRegistry
