from __future__ import annotations

import json
from typing import Any


def normalize(content: str) -> Any:
    """Parse JSON content into a Python structure. Raises json.JSONDecodeError on invalid input."""
    return json.loads(content)
