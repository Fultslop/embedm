"""Events emitted by FileCache."""

from dataclasses import dataclass

from embedm.infrastructure.events import EmbedmEvent


@dataclass(frozen=True)
class CacheEvent(EmbedmEvent):
    """Emitted by FileCache on cache activity. kind is 'hit', 'miss', or 'eviction'."""

    kind: str
    key: str
    elapsed: float
