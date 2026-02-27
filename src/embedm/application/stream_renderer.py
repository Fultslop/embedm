"""StreamRenderer — plain-text, line-by-line output for non-interactive (piped/CI) runs."""

from __future__ import annotations

import sys

from embedm.application.application_events import (
    FileCompleted,
    FileError,
    FilePlanError,
    FilePlanned,
    PlanningStarted,
    PluginsLoaded,
    SessionComplete,
    SessionStarted,
)
from embedm.application.configuration import Configuration
from embedm.application.console import RunSummary, _format_summary
from embedm.infrastructure.events import EventDispatcher
from embedm.infrastructure.file_util import to_relative


class StreamRenderer:
    """Subscribes to application events and produces plain, line-by-line output to stderr.

    No ANSI codes are emitted. Active when stdout is not a TTY or color is suppressed.
    """

    def __init__(self, config: Configuration) -> None:
        self._config = config

    def subscribe(self, dispatcher: EventDispatcher) -> None:
        dispatcher.subscribe(SessionStarted, self._on_session_started)
        dispatcher.subscribe(PluginsLoaded, self._on_plugins_loaded)
        dispatcher.subscribe(PlanningStarted, self._on_planning_started)
        dispatcher.subscribe(FilePlanned, self._on_file_planned)
        dispatcher.subscribe(FilePlanError, self._on_file_plan_error)
        dispatcher.subscribe(FileCompleted, self._on_file_completed)
        dispatcher.subscribe(FileError, self._on_file_error)
        dispatcher.subscribe(SessionComplete, self._on_session_complete)

    # --- event handlers ---

    def _on_session_started(self, event: SessionStarted) -> None:
        v = self._config.verbosity
        if v >= 1:
            print(f"Embedm v{event.version}", file=sys.stderr)
        if v >= 2:
            print(f"Config: {event.config_source}", file=sys.stderr)
            print(f"Input:  {event.input_type}", file=sys.stderr)
            print(f"Output: {event.output_type}", file=sys.stderr)

    def _on_plugins_loaded(self, event: PluginsLoaded) -> None:
        for e in event.errors:
            print(f"[ERR] {e}", file=sys.stderr)
        if self._config.verbosity >= 2 and not event.errors:
            print(
                f"{event.discovered} plugins discovered, {event.loaded} plugins loaded.",
                file=sys.stderr,
            )

    def _on_planning_started(self, event: PlanningStarted) -> None:
        if self._config.verbosity >= 2:
            print(f"Planning {event.file_count} file(s)", file=sys.stderr)

    def _on_file_planned(self, event: FilePlanned) -> None:
        if self._config.verbosity >= 2:
            rel = to_relative(event.file_path)
            print(f"  [{event.index + 1}/{event.total}] {rel}", file=sys.stderr)

    def _on_file_plan_error(self, event: FilePlanError) -> None:
        if self._config.verbosity >= 2:
            rel = to_relative(event.file_path)
            print(f"  [{event.index + 1}/{event.total}] {rel}", file=sys.stderr)
            print(f"  [ERR] {event.message}", file=sys.stderr)

    def _on_file_completed(self, event: FileCompleted) -> None:
        if self._config.verbosity >= 2:
            rel = to_relative(event.file_path)
            rel_out = to_relative(event.output_path)
            print(f"[OK] {event.elapsed:.2f}s  {rel} -> {rel_out}", file=sys.stderr)

    def _on_file_error(self, event: FileError) -> None:
        if self._config.verbosity >= 2:
            rel = to_relative(event.file_path)
            print(f"[ERR] {event.elapsed:.2f}s {rel}", file=sys.stderr)
            print(f"  {event.message}", file=sys.stderr)

    def _on_session_complete(self, event: SessionComplete) -> None:
        if self._config.verbosity < 1:
            return
        summary = RunSummary(
            ok_count=event.ok_count,
            error_count=event.error_count,
            warning_count=event.warning_count,
            elapsed_s=event.total_elapsed,
            files_written=event.files_written,
            output_target=event.output_target,
            is_verify=event.is_verify,
            up_to_date_count=event.up_to_date_count,
            stale_count=event.stale_count,
        )
        print(_format_summary(summary), file=sys.stderr)
