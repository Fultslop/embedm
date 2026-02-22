from __future__ import annotations

from typing import Any

import yaml


def normalize(content: str) -> Any:
    """Parse YAML content into a Python structure. Raises yaml.YAMLError on invalid input."""
    return yaml.safe_load(content)
