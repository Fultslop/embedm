"""Configuration file support for EmbedM.

This module handles loading and creation of embedm_config.yaml files
for directory-level processing configuration.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import os
import yaml


class ConfigValidationError(Exception):
    """Raised when config file has invalid values."""
    pass


@dataclass
class EmbedMConfig:
    """Configuration loaded from embedm_config.yaml.

    All fields are optional - None means the value should come from
    CLI args or class defaults.
    """

    # Limits section
    max_file_size: Optional[str] = None
    max_recursion: Optional[int] = None
    max_embeds_per_file: Optional[int] = None
    max_output_size: Optional[str] = None
    max_embed_text: Optional[str] = None

    # Output section
    output_directory: Optional[str] = None

    # Plugin section
    plugins: Optional[Any] = None  # Can be "*" (all), list of names, or dict with enabled/disabled

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbedMConfig':
        """Create config from parsed YAML dictionary.

        Args:
            data: Dictionary from YAML file

        Returns:
            EmbedMConfig instance
        """
        # Extract sections
        limits = data.get('limits', {})
        output = data.get('output', {})
        plugins = data.get('plugins')

        return cls(
            max_file_size=limits.get('max_file_size'),
            max_recursion=limits.get('max_recursion'),
            max_embeds_per_file=limits.get('max_embeds_per_file'),
            max_output_size=limits.get('max_output_size'),
            max_embed_text=limits.get('max_embed_text'),
            output_directory=output.get('directory'),
            plugins=plugins,
        )


def find_config_file(source_path: str) -> Optional[str]:
    """Find embedm_config.yaml in the source directory.

    Args:
        source_path: Path to check for config file

    Returns:
        Absolute path to config file if found, None otherwise
    """
    # Only look for config if source is a directory
    if not os.path.isdir(source_path):
        return None

    config_path = os.path.join(source_path, 'embedm_config.yaml')

    if os.path.isfile(config_path):
        return os.path.abspath(config_path)

    return None


def load_config(config_path: str) -> EmbedMConfig:
    """Load and validate config from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        EmbedMConfig instance

    Raises:
        ConfigValidationError: If config is invalid
        FileNotFoundError: If config file doesn't exist
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigValidationError(f"Invalid YAML in config file: {e}")

    if data is None:
        data = {}

    # Create config instance
    config = EmbedMConfig.from_dict(data)

    # Validate config values
    errors = validate_config(config)
    if errors:
        error_msg = "Config validation errors:\n  " + "\n  ".join(errors)
        raise ConfigValidationError(error_msg)

    return config


def validate_config(config: EmbedMConfig) -> List[str]:
    """Validate config values.

    Args:
        config: Config to validate

    Returns:
        List of error messages (empty if valid)
    """
    from .models import Limits

    errors = []

    # Validate size strings
    size_fields = [
        ('max_file_size', config.max_file_size),
        ('max_output_size', config.max_output_size),
        ('max_embed_text', config.max_embed_text),
    ]

    for field_name, value in size_fields:
        if value is not None:
            try:
                Limits.parse_size(value)
            except ValueError as e:
                errors.append(f"Invalid {field_name}: {e}")

    # Validate numeric ranges
    numeric_fields = [
        ('max_recursion', config.max_recursion),
        ('max_embeds_per_file', config.max_embeds_per_file),
    ]

    for field_name, value in numeric_fields:
        if value is not None:
            if not isinstance(value, int):
                errors.append(f"{field_name} must be an integer, got {type(value).__name__}")
            elif value < 0:
                errors.append(f"{field_name} must be >= 0, got {value}")

    # Validate plugins config
    if config.plugins is not None:
        if isinstance(config.plugins, str):
            if config.plugins != "*":
                errors.append("plugins must be '*' (enable all) or a list of plugin names")
        elif isinstance(config.plugins, list):
            if not all(isinstance(p, str) for p in config.plugins):
                errors.append("plugins list must contain only strings")
        else:
            errors.append("plugins must be '*' or a list, got " + type(config.plugins).__name__)

    return errors


def parse_plugins_config(plugins_config: Any) -> Optional[List[str]]:
    """Parse plugins configuration into list of enabled plugin names.

    Args:
        plugins_config: Plugin configuration from config file
                       Can be "*" (all plugins), list of names, or None

    Returns:
        None if all plugins should be enabled ("*" or None)
        List of plugin names if specific plugins should be enabled

    Examples:
        parse_plugins_config("*") -> None (enable all)
        parse_plugins_config(None) -> None (enable all)
        parse_plugins_config(["file", "toc"]) -> ["file", "toc"]
    """
    if plugins_config is None or plugins_config == "*":
        return None  # Enable all plugins

    if isinstance(plugins_config, list):
        return plugins_config  # Enable specific plugins

    # Invalid format (should have been caught by validate_config)
    return None


def generate_default_config() -> str:
    """Generate default config YAML content with documentation.

    Returns:
        YAML string with comments and default values
    """
    return """# EmbedM Configuration File
# This file configures default processing limits and output settings.
# CLI arguments will override these values.

# Safety Limits
limits:
  # Maximum size of input files (supports: 1MB, 1KB, 1024, etc.)
  max_file_size: "1MB"

  # Maximum recursion depth for embedded markdown files
  max_recursion: 8

  # Maximum number of embeds per file
  max_embeds_per_file: 100

  # Maximum size of generated output files
  max_output_size: "10MB"

  # Maximum size of embedded text snippets
  max_embed_text: "2KB"

# Output Configuration
output:
  # Output directory for compiled files (relative to this config file)
  directory: "compiled"

# Plugin Configuration
# Controls which plugins are enabled for processing embeds
plugins: "*"  # "*" = enable all discovered plugins (default)
# Alternatively, specify a list of plugin names to enable:
# plugins:
#   - file
#   - layout
#   - toc
"""


def prompt_create_config(directory: str) -> bool:
    """Prompt user to create config file interactively.

    Args:
        directory: Directory where config should be created

    Returns:
        True if config was created, False if user declined
    """
    print(f"\n📋 No embedm_config.yaml found in {os.path.basename(directory)}")
    print("   This config file stores processing limits and output settings.")

    try:
        response = input("   Create one now? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n   Continuing with default settings...")
        return False

    if response in ['y', 'yes']:
        config_path = os.path.join(directory, 'embedm_config.yaml')
        default_yaml = generate_default_config()

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(default_yaml)
            return True
        except OSError as e:
            print(f"   ⚠️  Could not create config file: {e}")
            print("   Continuing with default settings...")
            return False

    print("   Continuing with default settings...")
    return False
