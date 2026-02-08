"""Tests for configuration file support."""

import os
import tempfile
import pytest
import yaml
from embedm.config import (
    EmbedMConfig,
    find_config_file,
    load_config,
    validate_config,
    generate_default_config,
    ConfigValidationError
)
from embedm.cli import create_limits
from embedm.models import Limits


class TestConfigLoading:
    """Test config file discovery and loading."""

    def test_find_config_in_directory(self, tmp_path):
        """Test finding config file in directory."""
        # Create a config file
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text("limits:\n  max_recursion: 5\n")

        # Should find it
        found = find_config_file(str(tmp_path))
        assert found is not None
        assert os.path.basename(found) == "embedm_config.yaml"

    def test_find_config_not_in_directory(self, tmp_path):
        """Test when config file doesn't exist."""
        found = find_config_file(str(tmp_path))
        assert found is None

    def test_find_config_for_file_returns_none(self, tmp_path):
        """Test that config search doesn't work for files."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        found = find_config_file(str(test_file))
        assert found is None

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid config file."""
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text("""
limits:
  max_file_size: "5MB"
  max_recursion: 10
  max_embeds_per_file: 200

output:
  directory: "output"
""")

        config = load_config(str(config_file))
        assert config.max_file_size == "5MB"
        assert config.max_recursion == 10
        assert config.max_embeds_per_file == 200
        assert config.output_directory == "output"

    def test_load_partial_config(self, tmp_path):
        """Test loading config with only some values set."""
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text("""
limits:
  max_recursion: 5
""")

        config = load_config(str(config_file))
        assert config.max_recursion == 5
        assert config.max_file_size is None
        assert config.output_directory is None

    def test_load_empty_config(self, tmp_path):
        """Test loading an empty config file."""
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text("")

        config = load_config(str(config_file))
        assert config.max_recursion is None
        assert config.max_file_size is None

    def test_load_missing_file_raises_error(self):
        """Test that loading a non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    def test_load_invalid_yaml_raises_error(self, tmp_path):
        """Test that invalid YAML raises ConfigValidationError."""
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigValidationError, match="Invalid YAML"):
            load_config(str(config_file))

    def test_load_invalid_values_raises_error(self, tmp_path):
        """Test that invalid config values raise ConfigValidationError."""
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text("""
limits:
  max_file_size: "invalid_size"
""")

        with pytest.raises(ConfigValidationError, match="Invalid max_file_size"):
            load_config(str(config_file))


class TestConfigValidation:
    """Test config validation logic."""

    def test_validate_valid_config(self):
        """Test that valid config passes validation."""
        config = EmbedMConfig(
            max_file_size="1MB",
            max_recursion=8,
            max_embeds_per_file=100
        )

        errors = validate_config(config)
        assert len(errors) == 0

    def test_validate_invalid_size_format(self):
        """Test that invalid size format is caught."""
        config = EmbedMConfig(max_file_size="not_a_size")

        errors = validate_config(config)
        assert len(errors) > 0
        assert any("max_file_size" in e for e in errors)

    def test_validate_negative_recursion(self):
        """Test that negative recursion is caught."""
        config = EmbedMConfig(max_recursion=-5)

        errors = validate_config(config)
        assert len(errors) > 0
        assert any("max_recursion" in e and ">= 0" in e for e in errors)

    def test_validate_invalid_type(self):
        """Test that invalid types are caught."""
        config = EmbedMConfig(max_recursion="not_an_int")

        errors = validate_config(config)
        assert len(errors) > 0
        assert any("max_recursion" in e and "integer" in e for e in errors)


class TestConfigGeneration:
    """Test config file generation."""

    def test_generate_default_config_is_valid_yaml(self):
        """Test that generated config is valid YAML."""
        config_yaml = generate_default_config()

        # Should parse without errors
        data = yaml.safe_load(config_yaml)
        assert data is not None
        assert 'limits' in data
        assert 'output' in data

    def test_generate_default_config_has_all_fields(self):
        """Test that generated config has all expected fields."""
        config_yaml = generate_default_config()
        data = yaml.safe_load(config_yaml)

        # Check limits section
        assert 'max_file_size' in data['limits']
        assert 'max_recursion' in data['limits']
        assert 'max_embeds_per_file' in data['limits']
        assert 'max_output_size' in data['limits']
        assert 'max_embed_text' in data['limits']

        # Check output section
        assert 'directory' in data['output']

    def test_generated_config_can_be_loaded(self, tmp_path):
        """Test that generated config can be loaded back."""
        config_yaml = generate_default_config()

        # Write to file
        config_file = tmp_path / "embedm_config.yaml"
        config_file.write_text(config_yaml)

        # Should load without errors
        config = load_config(str(config_file))
        assert config.max_file_size == "1MB"
        assert config.max_recursion == 8
        assert config.output_directory == "compiled"

    def test_generated_config_has_comments(self):
        """Test that generated config includes documentation comments."""
        config_yaml = generate_default_config()

        # Should have comment lines
        assert '#' in config_yaml
        assert 'EmbedM Configuration File' in config_yaml


class TestLimitsPrecedence:
    """Test precedence of CLI args > config > defaults."""

    def test_cli_overrides_config(self):
        """Test that CLI args override config values."""
        from argparse import Namespace

        config = EmbedMConfig(max_recursion=5, max_file_size="2MB")
        args = Namespace(
            max_recursion=10,  # CLI override
            max_file_size="3MB",  # CLI override
            max_embeds=None,
            max_output_size=None,
            max_embed_text=None
        )

        limits = create_limits(args, config)

        assert limits.max_recursion == 10  # CLI value
        assert limits.max_file_size == Limits.parse_size("3MB")  # CLI value

    def test_config_overrides_defaults(self):
        """Test that config values override defaults."""
        from argparse import Namespace

        config = EmbedMConfig(max_recursion=5, max_file_size="2MB")
        args = Namespace(
            max_recursion=None,  # Not set via CLI
            max_file_size=None,  # Not set via CLI
            max_embeds=None,
            max_output_size=None,
            max_embed_text=None
        )

        limits = create_limits(args, config)

        assert limits.max_recursion == 5  # Config value
        assert limits.max_file_size == Limits.parse_size("2MB")  # Config value

    def test_defaults_when_no_config(self):
        """Test that defaults are used when no config or CLI args."""
        from argparse import Namespace

        args = Namespace(
            max_recursion=None,
            max_file_size=None,
            max_embeds=None,
            max_output_size=None,
            max_embed_text=None
        )

        limits = create_limits(args, config=None)

        # Should use defaults
        assert limits.max_recursion == 8
        assert limits.max_file_size == Limits.parse_size("1MB")
        assert limits.max_embeds_per_file == 100
        assert limits.max_output_size == Limits.parse_size("10MB")
        assert limits.max_embed_text == Limits.parse_size("2KB")

    def test_partial_config_partial_cli(self):
        """Test mixed precedence with partial config and CLI."""
        from argparse import Namespace

        config = EmbedMConfig(
            max_recursion=5,
            max_file_size="2MB"
            # Other fields None
        )
        args = Namespace(
            max_recursion=10,  # CLI override
            max_file_size=None,  # Use config
            max_embeds=50,  # CLI override
            max_output_size=None,  # Use default
            max_embed_text=None
        )

        limits = create_limits(args, config)

        assert limits.max_recursion == 10  # CLI
        assert limits.max_file_size == Limits.parse_size("2MB")  # Config
        assert limits.max_embeds_per_file == 50  # CLI
        assert limits.max_output_size == Limits.parse_size("10MB")  # Default


class TestOutputDirectory:
    """Test output directory handling from config."""

    def test_output_directory_from_config(self, tmp_path):
        """Test that output directory is read from config."""
        config = EmbedMConfig(output_directory="my_output")
        assert config.output_directory == "my_output"

    def test_output_directory_none_when_not_set(self):
        """Test that output directory is None when not in config."""
        config = EmbedMConfig()
        assert config.output_directory is None
