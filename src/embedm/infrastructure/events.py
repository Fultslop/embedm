"""Base event type and synchronous event dispatcher."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class EmbedmEvent:
    """Base class for all embedm events."""


class EventDispatcher:
    """Minimal synchronous publish/subscribe event bus.

    Producers call emit() with a typed event instance. Subscribers register
    per event type via subscribe(). Events are dispatched to all listeners
    registered for that exact type, in registration order, synchronously on
    the calling thread. No verbosity filtering — that is the subscriber's
    responsibility.
    """

    def __init__(self) -> None:
        self._listeners: dict[type[EmbedmEvent], list[Callable[[EmbedmEvent], None]]] = defaultdict(list)

    def subscribe(self, event_type: type[EmbedmEvent], listener: Callable[[EmbedmEvent], None]) -> None:
        """Register listener to be called whenever an event of event_type is emitted."""
        self._listeners[event_type].append(listener)

    def emit(self, event: EmbedmEvent) -> None:
        """Dispatch event to all listeners registered for its exact type."""
        for listener in self._listeners[type(event)]:
            listener(event)
