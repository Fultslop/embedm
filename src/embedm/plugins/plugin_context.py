from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_configuration import PluginConfiguration

if TYPE_CHECKING:
    from embedm.plugins.plugin_registry import PluginRegistry


@dataclass
class PluginContext:
    """Runtime context passed to every plugin's transform method.

    Bundles the three infrastructure dependencies so plugins receive a single
    object instead of three separate parameters.  Plugins that do not need
    file_cache or plugin_registry can declare ``context=None`` and ignore it.
    """

    file_cache: FileCache
    plugin_registry: PluginRegistry | None = None
    plugin_config: PluginConfiguration | None = None
