"""ANSI escape-code helpers for terminal color and cursor control."""

from __future__ import annotations

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def colorize(text: str, code: str, use_color: bool) -> str:
    """Wrap text in an ANSI color code when use_color is True."""
    return f"{code}{text}{RESET}" if use_color else text


def cursor_up(n: int) -> str:
    """ANSI sequence to move the cursor up n lines."""
    return f"\033[{n}A" if n > 0 else ""


def clear_to_end() -> str:
    """ANSI sequence to clear from the cursor to the end of the screen."""
    return "\033[J"
