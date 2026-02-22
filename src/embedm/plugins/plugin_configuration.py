from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PluginConfiguration:
    """Configuration properties available to plugins during transformation."""

    max_embed_size: int
    max_recursion: int
    compiled_dir: str = ""
    plugin_sequence: tuple[str, ...] = ()
    plugin_settings: dict[str, dict[str, Any]] = field(default_factory=dict)
