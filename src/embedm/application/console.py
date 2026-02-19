from __future__ import annotations

import sys
from collections.abc import Sequence
from importlib.metadata import version

from embedm.application.application_resources import str_resources
from embedm.domain.status_level import Status


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


def prompt_continue() -> bool:
    """Prompt the user to continue or abort compilation. Returns True to continue."""
    try:
        response = input(str_resources.continue_compilation)
        return response.strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False
