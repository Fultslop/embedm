from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from importlib.metadata import version
from pathlib import Path

from embedm.application.application_resources import str_resources
from embedm.application.configuration import Configuration
from embedm.domain.plan_node import PlanNode
from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.plugin_registry import PluginRegistry


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


def present_title() -> None:
    """Print the application banner."""
    print(f"embedm v{version('embedm')}")


def present_errors(errors: Sequence[Status] | str) -> None:
    """Print errors to stderr."""
    if isinstance(errors, str):
        print(f"error: {errors}", file=sys.stderr)
        return
    for error in errors:
        print(f"error: {error.description}", file=sys.stderr)


def present_result(result: str) -> None:
    """Print compilation result to stdout."""
    print(result, end="")


def present_verify_status(status: str, path: str) -> None:
    """Print a verify-mode per-file status line to stderr (always, not behind --verbose)."""
    print(f"[{status.upper()}] {path}", file=sys.stderr)


def present_file_progress(file_path: str, plan_root: PlanNode) -> None:
    """Print a per-file progress line to stderr at verbosity level 2."""
    label = _worst_status_label(plan_root.status)
    print(f"  {Path(file_path).name}  [{label}]", file=sys.stderr)


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


def verbose_section(title: str) -> None:
    """Print a section header to stderr."""
    print(f"\n--- {title} ---", file=sys.stderr)


def verbose_config(config: Configuration) -> None:
    """Print the current working directory and all configuration fields to stderr."""
    _vprint(f"cwd:                {Path.cwd()}")
    _vprint(f"config_file:        {config.config_file or '(none)'}")
    _vprint(f"input_mode:         {config.input_mode.value}")
    input_display = config.input if len(config.input) <= 60 else config.input[:57] + "..."
    _vprint(f"input:              {input_display}")
    _vprint(f"output_file:        {config.output_file or '(none)'}")
    _vprint(f"output_directory:   {config.output_directory or '(none)'}")
    _vprint(f"max_file_size:      {config.max_file_size}")
    _vprint(f"max_recursion:      {config.max_recursion}")
    _vprint(f"max_memory:         {config.max_memory}")
    _vprint(f"max_embed_size:     {config.max_embed_size}")
    _vprint(f"root_directive:     {config.root_directive_type}")
    _vprint(f"is_accept_all:      {config.is_accept_all}")
    _vprint(f"is_dry_run:         {config.is_dry_run}")
    _vprint(f"is_verify:          {config.is_verify}")
    _vprint(f"line_endings:       {config.line_endings}")
    _vprint(f"verbosity:          {config.verbosity}")
    _vprint("plugin_sequence:")
    for module in config.plugin_sequence:
        _vprint(f"  {module}")


def verbose_plugins(registry: PluginRegistry, config: Configuration) -> None:
    """Print plugin discovery results to stderr."""
    _vprint(f"sequence (from config): {len(config.plugin_sequence)} modules")

    _vprint(f"discovered:         {len(registry.discovered)} entry points")
    for name, module in registry.discovered:
        _vprint(f"  {name:<24} ({module})")

    if registry.skipped:
        _vprint(f"skipped:            {len(registry.skipped)}")
        for name, module in registry.skipped:
            config_entry = next((m for m in config.plugin_sequence if m.strip().rstrip(",") == module), None)
            if config_entry and config_entry != module:
                _vprint(f"  {name:<24} entry: {module}")
                _vprint(f"  {'':<24} config: '{config_entry}'  <- mismatch")
            else:
                _vprint(f"  {name:<24} ({module})")

    _vprint(f"loaded:             {registry.count}")
    for plugin in registry.lookup.values():
        _vprint(f"  {plugin.name:<24} type: {plugin.directive_type:<20} ({plugin.__class__.__module__})")


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


def verbose_output_path(path: str) -> None:
    """Print the full path of a written output file to stderr."""
    _vprint(f"output: {path}")


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


def present_plugin_list(registry: PluginRegistry, issues: list[Status]) -> None:
    """Print a formatted plugin health report to stdout."""
    loaded = list(registry.lookup.values())
    print(f"plugins ({len(loaded)} loaded):")
    if loaded:
        dt_width = max(len(p.directive_type) for p in loaded)
        name_width = max(len(p.name) for p in loaded)
        for plugin in loaded:
            module = plugin.__class__.__module__
            print(f"  {plugin.directive_type:<{dt_width}}  {plugin.name:<{name_width}}  {module}")

    if registry.skipped:
        print(f"\nskipped ({len(registry.skipped)} not in plugin_sequence):")
        for name, module in registry.skipped:
            print(f"  {name}  ({module})")

    if issues:
        print(f"\nissues ({len(issues)}):")
        for issue in issues:
            prefix = "error" if issue.level in (StatusLevel.ERROR, StatusLevel.FATAL) else "warning"
            print(f"  {prefix}: {issue.description}")


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
