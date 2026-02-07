"""YAML embed block parsing utilities."""

import yaml
from typing import Optional, Dict


def parse_yaml_embed_block(content: str) -> Optional[tuple[str, Dict]]:
    """
    Parse YAML embed block content
    Returns: (embed_type, properties_dict) or None if not a valid embed block

    Expected format:
    ```yaml
    type: embed.file
    source: path/to/file.py
    region: L10-20
    line_numbers: html
    title: My Title
    ```
    """
    try:
        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            return None

        embed_type = data.get('type', '')

        # Check if this is an embed block
        if not embed_type.startswith('embed.'):
            return None

        # Extract the actual type (e.g., 'file' from 'embed.file')
        actual_type = embed_type[6:]  # Remove 'embed.' prefix

        # Return type and all properties
        return (actual_type, data)

    except yaml.YAMLError:
        return None
