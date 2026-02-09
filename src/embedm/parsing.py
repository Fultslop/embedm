"""YAML embed block parsing utilities."""

import yaml
from typing import Optional, Dict


def parse_yaml_embed_block(content: str) -> Optional[tuple[str, Dict]]:
    """
    Parse YAML embed block content
    Returns: (embed_type, properties_dict) or None if not a valid embed block

    Expected format:
    ```yaml embedm
    type: file
    source: path/to/file.py
    lines: L10-20
    line_numbers: html
    title: My Title
    ```
    """
    try:
        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            return None

        embed_type = data.get('type', '')

        # Check if type is present and non-empty
        if not embed_type:
            return None

        # Return type and all properties
        return (embed_type, data)

    except yaml.YAMLError:
        return None
