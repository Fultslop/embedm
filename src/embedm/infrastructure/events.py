"""Typed event catalog and synchronous event dispatcher for the embedm event system."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from embedm.domain.status_level import StatusLevel


@dataclass(frozen=True)
class EmbedmEvent:
    """Base class for all embedm events."""


# --- Session lifecycle ---


@dataclass(frozen=True)
class SessionStarted(EmbedmEvent):
    """Emitted once at the start of a run, before any processing."""

    version: str
    config_source: str
    input_type: str
    output_type: str


@dataclass(frozen=True)
class SessionComplete(EmbedmEvent):
    """Emitted once after all processing has finished."""

    ok_count: int
    error_count: int
    total_elapsed: float


# --- Plugin loading ---


@dataclass(frozen=True)
class PluginsLoaded(EmbedmEvent):
    """Emitted after the plugin registry has been populated."""

    discovered: int
    loaded: int
    errors: list[str]


# --- Planning ---


@dataclass(frozen=True)
class PlanningStarted(EmbedmEvent):
    """Emitted before the first file is planned."""

    file_count: int


@dataclass(frozen=True)
class FilePlanned(EmbedmEvent):
    """Emitted after a file has been successfully planned."""

    file_path: str
    index: int
    total: int


@dataclass(frozen=True)
class FilePlanError(EmbedmEvent):
    """Emitted when planning a file produces an error."""

    file_path: str
    index: int
    total: int
    message: str


@dataclass(frozen=True)
class PlanningComplete(EmbedmEvent):
    """Emitted after all files have been planned."""

    file_count: int
    error_count: int


# --- Compilation ---


@dataclass(frozen=True)
class CompilationStarted(EmbedmEvent):
    """Emitted before the first file is compiled."""

    file_count: int


@dataclass(frozen=True)
class FileStarted(EmbedmEvent):
    """Emitted when compilation of a file begins."""

    file_path: str
    node_count: int
    index: int
    total: int


@dataclass(frozen=True)
class NodeCompiled(EmbedmEvent):
    """Emitted after each node in a file's plan tree is compiled."""

    file_path: str
    node_index: int
    node_count: int
    elapsed: float


@dataclass(frozen=True)
class FileCompleted(EmbedmEvent):
    """Emitted when a file compiles successfully."""

    file_path: str
    output_path: str
    elapsed: float
    index: int
    total: int


@dataclass(frozen=True)
class FileError(EmbedmEvent):
    """Emitted when a file fails to compile. message is the exception message, not the traceback."""

    file_path: str
    message: str
    elapsed: float
    index: int
    total: int


@dataclass(frozen=True)
class CompilationComplete(EmbedmEvent):
    """Emitted after all files have been compiled."""

    ok_count: int
    error_count: int


# --- Infrastructure ---


@dataclass(frozen=True)
class CacheEvent(EmbedmEvent):
    """Emitted by FileCache on cache activity. kind is 'hit', 'miss', or 'eviction'."""

    kind: str
    key: str
    elapsed: float


# --- Plugin diagnostics ---


@dataclass(frozen=True)
class PluginDiagnostic(EmbedmEvent):
    """Emitted by a plugin to report a warning or non-fatal error during transformation."""

    plugin_name: str
    file_path: str
    level: StatusLevel
    message: str


# --- Dispatcher ---


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
