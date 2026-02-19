from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from embedm.domain.domain_resources import str_resources
from embedm.domain.status_level import Status, StatusLevel

from .configuration import (
    CONFIG_FILE_NAME,
    DEFAULT_MAX_EMBED_SIZE,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_MAX_MEMORY,
    DEFAULT_MAX_RECURSION,
    DEFAULT_PLUGIN_SEQUENCE,
    DEFAULT_ROOT_DIRECTIVE_TYPE,
    Configuration,
)

# fields that can appear in the config file, mapped to their expected type
_CONFIG_FIELDS: dict[str, type] = {
    "max_file_size": int,
    "max_recursion": int,
    "max_memory": int,
    "max_embed_size": int,
    "root_directive_type": str,
    "plugin_sequence": list,
}

_DEFAULT_CONFIG_TEMPLATE = f"""\
# embedm configuration file
# see https://github.com/embedm/embedm for documentation

# max file size in bytes
max_file_size: {DEFAULT_MAX_FILE_SIZE}

# max recursion depth for nested embeds
max_recursion: {DEFAULT_MAX_RECURSION}

# max memory for file cache in bytes
max_memory: {DEFAULT_MAX_MEMORY}

# max embed size in bytes
max_embed_size: {DEFAULT_MAX_EMBED_SIZE}

# directive type used for root plan nodes
root_directive_type: {DEFAULT_ROOT_DIRECTIVE_TYPE}

# plugin load order
plugin_sequence:
"""


def _build_default_template() -> str:
    """Build the full default config template including the plugin sequence list."""
    lines = _DEFAULT_CONFIG_TEMPLATE
    for plugin in DEFAULT_PLUGIN_SEQUENCE:
        lines += f"  - {plugin}\n"
    return lines


def generate_default_config(directory: str) -> tuple[str, list[Status]]:
    """Generate a default embedm-config.yaml in the given directory."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return "", [Status(StatusLevel.ERROR, f"directory '{directory}' does not exist")]

    config_path = dir_path / CONFIG_FILE_NAME
    if config_path.exists():
        return "", [Status(StatusLevel.ERROR, f"'{config_path}' already exists")]

    config_path.write_text(_build_default_template(), encoding="utf-8")
    return str(config_path), []


def load_config_file(path: str) -> tuple[Configuration, list[Status]]:
    """Load a config file and return a Configuration with overridden fields."""
    config_path = Path(path)
    if not config_path.is_file():
        return Configuration(), [Status(StatusLevel.ERROR, f"config file '{path}' not found")]

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return Configuration(), [Status(StatusLevel.ERROR, f"failed to parse '{path}': {e}")]

    if raw is None:
        return Configuration(), []

    if not isinstance(raw, dict):
        return Configuration(), [Status(StatusLevel.ERROR, f"config file '{path}' must be a YAML mapping")]

    return _parse_config(raw)


def discover_config(input_path: str) -> str | None:
    """Look for embedm-config.yaml in the input file's directory."""
    parent = Path(input_path).resolve().parent
    config_path = parent / CONFIG_FILE_NAME
    if config_path.is_file():
        return str(config_path)
    return None


def _parse_config(raw: dict[str, Any]) -> tuple[Configuration, list[Status]]:
    """Validate and parse a raw YAML dict into a Configuration."""
    errors: list[Status] = []
    overrides: dict[str, Any] = {}

    for key, value in raw.items():
        if key not in _CONFIG_FIELDS:
            errors.append(Status(StatusLevel.WARNING, f"unknown config key '{key}'"))
            continue

        expected_type = _CONFIG_FIELDS[key]
        if not isinstance(value, expected_type):
            msg = f"config key '{key}' must be {expected_type.__name__}, got {type(value).__name__}"
            errors.append(Status(StatusLevel.ERROR, msg))
            continue

        overrides[key] = value

    has_errors = any(s.level == StatusLevel.ERROR for s in errors)
    if has_errors:
        return Configuration(), errors

    config = Configuration(**overrides)

    if config.max_memory <= config.max_file_size:
        msg = str_resources.config_memory_must_exceed_file_size.format(
            max_memory=config.max_memory, max_file_size=config.max_file_size
        )
        return Configuration(), [Status(StatusLevel.ERROR, msg)]

    return config, errors
