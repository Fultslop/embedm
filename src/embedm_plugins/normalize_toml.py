from __future__ import annotations

import tomllib
from typing import Any


def normalize(content: str) -> Any:
    """Parse TOML content into a Python structure. Raises tomllib.TOMLDecodeError on invalid input."""
    return tomllib.loads(content)
