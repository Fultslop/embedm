from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from embedm.application.application_resources import str_resources
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel


class ContinueChoice(Enum):
    YES = "yes"
    NO = "no"
    ALWAYS = "always"
    EXIT = "exit"


@dataclass
class RunSummary:
    """Tracks per-run output counts for the summary line."""

    files_written: int = 0
    output_target: str = "stdout"
    ok_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    elapsed_s: float = 0.0
    # verify-mode counters
    is_verify: bool = False
    up_to_date_count: int = 0
    stale_count: int = 0


def prompt_continue() -> ContinueChoice:
    """Prompt the user to continue, abort, accept all, or exit. Returns the user's choice."""
    try:
        response = input(str_resources.continue_compilation).strip().lower()
        if response in ("a", "always"):
            return ContinueChoice.ALWAYS
        if response in ("y", "yes"):
            return ContinueChoice.YES
        if response in ("x", "exit"):
            return ContinueChoice.EXIT
        return ContinueChoice.NO
    except (EOFError, KeyboardInterrupt):
        return ContinueChoice.EXIT


# --- verbose output ---


def verbose_plan_tree(node: PlanNode, indent: int = 0) -> None:
    """Print a plan node and its children as an indented tree to stderr."""
    prefix = "  " * indent
    label = _worst_status_label(node.status)

    if indent == 0:
        print(f"{prefix}[{label}] {node.directive.source}", file=sys.stderr)
    else:
        source = f": {node.directive.source}" if node.directive.source else ""
        print(f"{prefix}[{label}] {node.directive.type}{source}", file=sys.stderr)

    for s in node.status:
        if s.level in (StatusLevel.WARNING, StatusLevel.ERROR, StatusLevel.FATAL):
            print(f"{prefix}  -> {s.description}", file=sys.stderr)

    for child in node.children or []:
        verbose_plan_tree(child, indent + 1)


def verbose_summary(summary: RunSummary) -> None:
    """Print the full run summary to stderr."""
    print(_format_summary(summary), file=sys.stderr)


def present_run_hint(summary: RunSummary) -> None:
    """Print the summary + verbose hint to stderr when errors are present in non-verbose mode."""
    print(f"{_format_summary(summary)}. {str_resources.verbose_hint}", file=sys.stderr)


def present_warnings(warnings: list[Status]) -> None:
    """Print warning-level statuses to stderr."""
    for w in warnings:
        print(f"warning: {w.description}", file=sys.stderr)


def make_cache_event_handler() -> Callable[[str, str, float], None]:
    """Return a callable that prints cache events to stderr."""

    def handler(path: str, event: str, elapsed_s: float) -> None:
        if event == "miss":
            _vprint(f"[cache miss] {elapsed_s:.3f}s — {path}")
        else:
            _vprint(f"[cache {event}] {path}")

    return handler


def verbose_timing(method: str, directive_type: str, source: str, elapsed_s: float) -> None:
    """Print a plugin method timing line to stderr."""
    _vprint(f"[{method}] {elapsed_s:.3f}s — {directive_type}: {source}")


# --- helpers ---


def _vprint(line: str) -> None:
    print(f"  {line}", file=sys.stderr)


def _worst_status_label(statuses: list[Status]) -> str:
    if any(s.level == StatusLevel.FATAL for s in statuses):
        return "FATAL"
    if any(s.level == StatusLevel.ERROR for s in statuses):
        return "ERROR"
    if any(s.level == StatusLevel.WARNING for s in statuses):
        return "WARN"
    return "OK"


def _format_summary(summary: RunSummary) -> str:
    if summary.is_verify:
        checked = summary.up_to_date_count + summary.stale_count
        noun = "file" if checked == 1 else "files"
        return (
            f"embedm verify complete, {checked} {noun} checked, "
            f"{summary.up_to_date_count} up-to-date, {summary.stale_count} stale, "
            f"{summary.error_count} errors, completed in {summary.elapsed_s:.3f}s"
        )
    noun = "file" if summary.files_written == 1 else "files"
    target = f"to {summary.output_target}" if summary.output_target != "stdout" else "to stdout"
    return (
        f"embedm process complete, {summary.files_written} {noun} written {target}, "
        f"{summary.ok_count} ok, {summary.warning_count} warnings, {summary.error_count} errors, "
        f"completed in {summary.elapsed_s:.3f}s"
    )
