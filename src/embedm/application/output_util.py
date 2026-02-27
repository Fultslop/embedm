"""Direct I/O helpers used by orchestration for primary tool output."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from embedm.domain.status_level import Status, StatusLevel
from embedm.plugins.plugin_registry import PluginRegistry


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
