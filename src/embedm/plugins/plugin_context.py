from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.events import EventDispatcher
from embedm.infrastructure.file_cache import FileCache
from embedm.plugins.plugin_configuration import PluginConfiguration
from embedm.plugins.plugin_events import PluginDiagnostic

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
    events: EventDispatcher | None = None
    plugin_name: str = ""
    file_path: str = ""

    def emit_diagnostic(self, level: StatusLevel, message: str) -> None:
        """Emit a PluginDiagnostic event if an event dispatcher is attached."""
        if self.events is not None:
            self.events.emit(
                PluginDiagnostic(
                    plugin_name=self.plugin_name,
                    file_path=self.file_path,
                    level=level,
                    message=message,
                )
            )
