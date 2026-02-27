from dataclasses import dataclass, field

from embedm.infrastructure.events import EventDispatcher
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_registry import PluginRegistry

from .configuration import Configuration


@dataclass
class EmbedmContext:
    config: Configuration
    file_cache: FileCache
    plugin_registry: PluginRegistry
    accept_all: bool = False
    events: EventDispatcher = field(default_factory=EventDispatcher)
