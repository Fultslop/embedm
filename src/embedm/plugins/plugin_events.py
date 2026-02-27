"""Events emitted by plugins during transformation."""

from dataclasses import dataclass

from embedm.domain.status_level import StatusLevel
from embedm.infrastructure.events import EmbedmEvent


@dataclass(frozen=True)
class PluginDiagnostic(EmbedmEvent):
    """Emitted by a plugin to report a warning or non-fatal error during transformation."""

    plugin_name: str
    file_path: str
    level: StatusLevel
    message: str
