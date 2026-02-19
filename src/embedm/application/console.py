from __future__ import annotations

import sys
from collections.abc import Sequence
from enum import Enum
from importlib.metadata import version

from embedm.application.application_resources import str_resources
from embedm.domain.status_level import Status


class ContinueChoice(Enum):
    YES = "yes"
    NO = "no"
    ALWAYS = "always"


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


def prompt_continue() -> ContinueChoice:
    """Prompt the user to continue, abort, or accept all. Returns the user's choice."""
    try:
        response = input(str_resources.continue_compilation).strip().lower()
        if response in ("a", "always"):
            return ContinueChoice.ALWAYS
        if response in ("y", "yes"):
            return ContinueChoice.YES
        return ContinueChoice.NO
    except (EOFError, KeyboardInterrupt):
        return ContinueChoice.NO
