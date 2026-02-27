"""InteractiveRenderer — ANSI live-progress output for interactive (TTY) runs."""

from __future__ import annotations

import os
import sys
import time

from embedm.application.ansi import BOLD, CYAN, DIM, GREEN, RED, clear_to_end, colorize, cursor_up
from embedm.application.application_events import (
    CompilationStarted,
    FileCompleted,
    FileError,
    FilePlanError,
    FilePlanned,
    FileStarted,
    NodeCompiled,
    PlanningStarted,
    PluginsLoaded,
    SessionComplete,
    SessionStarted,
)
from embedm.application.configuration import Configuration
from embedm.application.console import RunSummary, _format_summary
from embedm.infrastructure.events import EventDispatcher
from embedm.infrastructure.file_util import to_relative


class InteractiveRenderer:
    """Subscribes to application events and produces ANSI live-progress output.

    Maintains a live section at the bottom of stderr that shows active files and
    their per-node progress percentage, overwriting in place on each update.
    Active when stdout is a TTY and color is not suppressed.
    """

    def __init__(self, config: Configuration) -> None:
        self._config = config
        self._use_color = not config.no_color and not os.environ.get("NO_COLOR")
        self._live_lines: int = 0
        self._compile_start: float = 0.0
        self._compile_done: int = 0
        self._compile_total: int = 0
        self._file_start_times: dict[str, float] = {}
        self._file_progress: dict[str, tuple[int, int]] = {}  # path → (node_index, node_count)
        self._error_lines: list[str] = []  # accumulated for re-listing at complete state

    def subscribe(self, dispatcher: EventDispatcher) -> None:
        dispatcher.subscribe(SessionStarted, self._on_session_started)
        dispatcher.subscribe(PluginsLoaded, self._on_plugins_loaded)
        dispatcher.subscribe(PlanningStarted, self._on_planning_started)
        dispatcher.subscribe(FilePlanned, self._on_file_planned)
        dispatcher.subscribe(FilePlanError, self._on_file_plan_error)
        dispatcher.subscribe(CompilationStarted, self._on_compilation_started)
        dispatcher.subscribe(FileStarted, self._on_file_started)
        dispatcher.subscribe(NodeCompiled, self._on_node_compiled)
        dispatcher.subscribe(FileCompleted, self._on_file_completed)
        dispatcher.subscribe(FileError, self._on_file_error)
        dispatcher.subscribe(SessionComplete, self._on_session_complete)

    # --- event handlers ---

    def _on_session_started(self, event: SessionStarted) -> None:
        v = self._config.verbosity
        if v >= 1:
            print(colorize(f"Embedm v{event.version}", BOLD, self._use_color), file=sys.stderr)
        if v >= 2:
            print(colorize(f"Config: {event.config_source}", DIM, self._use_color), file=sys.stderr)
            print(colorize(f"Input:  {event.input_type}", DIM, self._use_color), file=sys.stderr)
            print(colorize(f"Output: {event.output_type}", DIM, self._use_color), file=sys.stderr)

    def _on_plugins_loaded(self, event: PluginsLoaded) -> None:
        for e in event.errors:
            print(colorize(f"[ERR] {e}", RED, self._use_color), file=sys.stderr)
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
            err_line = f"  [ERR] {event.message}"
            print(colorize(err_line, RED, self._use_color), file=sys.stderr)

    def _on_compilation_started(self, event: CompilationStarted) -> None:
        self._compile_start = time.perf_counter()
        self._compile_done = 0
        self._compile_total = event.file_count

    def _on_file_started(self, event: FileStarted) -> None:
        if self._config.verbosity >= 2:
            self._start_file(event.file_path, event.node_count)
            self._redraw_live()

    def _on_node_compiled(self, event: NodeCompiled) -> None:
        if self._config.verbosity >= 2 and event.file_path in self._file_progress:
            self._file_progress[event.file_path] = (event.node_index, event.node_count)
            self._redraw_live()

    def _on_file_completed(self, event: FileCompleted) -> None:
        if self._config.verbosity >= 2:
            self._erase_live()
            rel = to_relative(event.file_path)
            rel_out = to_relative(event.output_path)
            ok_tag = colorize("[OK]", GREEN, self._use_color)
            print(f"{ok_tag} {event.elapsed:.2f}s  {rel} -> {rel_out}", file=sys.stderr)
            self._compile_done += 1
            self._file_progress.pop(event.file_path, None)
            self._file_start_times.pop(event.file_path, None)
            self._redraw_live()

    def _on_file_error(self, event: FileError) -> None:
        if self._config.verbosity >= 2:
            self._erase_live()
            rel = to_relative(event.file_path)
            err_tag = colorize("[ERR]", RED, self._use_color)
            line1 = f"{err_tag} {event.elapsed:.2f}s {rel}"
            line2 = f"  {event.message}"
            print(line1, file=sys.stderr)
            print(line2, file=sys.stderr)
            self._error_lines.extend([line1, line2])
            self._compile_done += 1
            self._file_progress.pop(event.file_path, None)
            self._file_start_times.pop(event.file_path, None)
            self._redraw_live()

    def _on_session_complete(self, event: SessionComplete) -> None:
        if self._config.verbosity < 1:
            return
        self._erase_live()

        # re-list errors at v2 when errors occurred (they may have scrolled out of view)
        if self._config.verbosity >= 2 and event.error_count > 0 and self._error_lines:
            for line in self._error_lines:
                print(line, file=sys.stderr)
            print(file=sys.stderr)

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

    # --- live section helpers ---

    def _erase_live(self) -> None:
        """Erase the current live section from the terminal."""
        if self._live_lines > 0:
            sys.stderr.write(cursor_up(self._live_lines) + clear_to_end())
            sys.stderr.flush()
            self._live_lines = 0

    def _redraw_live(self) -> None:
        """Erase previous live section and draw an updated one."""
        self._erase_live()
        lines: list[str] = []

        elapsed = time.perf_counter() - self._compile_start
        title = f"Embedm [{self._compile_done}/{self._compile_total}] {elapsed:.2f}s"
        lines.append(colorize(title, BOLD, self._use_color))

        for fp, (node_idx, node_total) in self._file_progress.items():
            pct = int(node_idx / node_total * 100) if node_total else 0
            file_elapsed = time.perf_counter() - self._file_start_times.get(fp, time.perf_counter())
            rel = to_relative(fp)
            progress = colorize(f"{rel}: {pct}%", CYAN, self._use_color)
            lines.append(f" - {progress} ({file_elapsed:.2f}s)")

        output = "\n".join(lines) + "\n"
        sys.stderr.write(output)
        sys.stderr.flush()
        self._live_lines = len(lines)

    def _start_file(self, file_path: str, node_count: int) -> None:
        """Register a file as active in the live section."""
        self._file_start_times[file_path] = time.perf_counter()
        self._file_progress[file_path] = (0, node_count)
