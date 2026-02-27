"""Renderer protocol — implemented by any output backend."""

from __future__ import annotations

from typing import Protocol

from embedm.infrastructure.events import EventDispatcher


class Renderer(Protocol):
    def subscribe(self, dispatcher: EventDispatcher) -> None: ...
