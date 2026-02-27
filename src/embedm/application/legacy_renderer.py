"""LegacyRenderer — reproduces the current console output via event subscriptions."""

from __future__ import annotations

import sys
from pathlib import Path

from embedm.application.application_events import (
    FileProcessed,
    PluginsLoaded,
    SessionComplete,
    SessionStarted,
)
from embedm.application.configuration import Configuration
from embedm.application.console import RunSummary, present_run_hint, verbose_summary
from embedm.infrastructure.events import EventDispatcher


class LegacyRenderer:
    """Subscribes to application events and renders them using the existing console functions."""

    def __init__(self, config: Configuration) -> None:
        self._config = config

    def subscribe(self, dispatcher: EventDispatcher) -> None:
        dispatcher.subscribe(SessionStarted, self._on_session_started)
        dispatcher.subscribe(PluginsLoaded, self._on_plugins_loaded)
        dispatcher.subscribe(FileProcessed, self._on_file_processed)
        dispatcher.subscribe(SessionComplete, self._on_session_complete)

    def _on_session_started(self, event: SessionStarted) -> None:
        if self._config.verbosity >= 1:
            print(f"embedm v{event.version}")

    def _on_plugins_loaded(self, event: PluginsLoaded) -> None:
        for w in event.warnings:
            print(f"warning: {w}", file=sys.stderr)

    def _on_file_processed(self, event: FileProcessed) -> None:
        if self._config.verbosity == 2:
            name = Path(event.file_path).name
            print(f"  {name}  [{event.status_label}]", file=sys.stderr)

    def _on_session_complete(self, event: SessionComplete) -> None:
        if self._config.verbosity == 0:
            return
        summary = RunSummary(
            files_written=event.files_written,
            output_target=event.output_target,
            ok_count=event.ok_count,
            warning_count=event.warning_count,
            error_count=event.error_count,
            elapsed_s=event.total_elapsed,
            is_verify=event.is_verify,
            up_to_date_count=event.up_to_date_count,
            stale_count=event.stale_count,
        )
        if event.error_count > 0 and self._config.is_accept_all and self._config.verbosity < 2:
            present_run_hint(summary)
        else:
            verbose_summary(summary)
