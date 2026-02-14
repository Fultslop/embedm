from dataclasses import dataclass


@dataclass(frozen=True)
class PluginConfiguration:
    """Configuration properties available to plugins during transformation."""

    max_embed_size: int
    max_recursion: int
