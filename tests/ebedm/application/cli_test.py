from __future__ import annotations

from unittest.mock import patch

from embedm.application.cli import parse_command_line_arguments
from embedm.application.configuration import (
    DEFAULT_MAX_EMBED_SIZE,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_MAX_MEMORY,
    DEFAULT_MAX_RECURSION,
    DEFAULT_PLUGIN_SEQUENCE,
    InputMode,
)
from embedm.domain.status_level import StatusLevel

# --- file to stdout ---


def test_file_to_stdout() -> None:
    config, errors = parse_command_line_arguments(["my_content.md"])

    assert not errors
    assert config.input_mode == InputMode.FILE
    assert config.input == "my_content.md"
    assert config.output_file is None
    assert config.output_directory is None


# --- file to file ---


def test_file_to_file_short_flag() -> None:
    config, errors = parse_command_line_arguments(["my_content.md", "-o", "output.md"])

    assert not errors
    assert config.input == "my_content.md"
    assert config.output_file == "output.md"


def test_file_to_file_long_flag() -> None:
    config, errors = parse_command_line_arguments(["my_content.md", "--output-file", "output.md"])

    assert not errors
    assert config.output_file == "output.md"


# --- directory to directory ---


def test_dir_to_dir_short_flag() -> None:
    config, errors = parse_command_line_arguments(["./my_content", "-d", "./compiled"])

    assert not errors
    assert config.input_mode == InputMode.DIRECTORY
    assert config.input == "./my_content"
    assert config.output_directory == "./compiled"


def test_dir_to_dir_long_flag() -> None:
    config, errors = parse_command_line_arguments(["./src", "--output-dir", "./out"])

    assert not errors
    assert config.output_directory == "./out"


# --- config file ---


def test_config_short_flag() -> None:
    config, errors = parse_command_line_arguments(["input.md", "-c", "config.yaml"])

    assert not errors
    assert config.input == "input.md"


def test_config_long_flag() -> None:
    config, errors = parse_command_line_arguments(["input.md", "--config", "config.yaml"])

    assert not errors


# --- stdin ---


def test_stdin_to_stdout() -> None:
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "piped content"

        config, errors = parse_command_line_arguments([])

    assert not errors
    assert config.input_mode == InputMode.STDIN
    assert config.input == "piped content"
    assert config.output_file is None


def test_stdin_to_file() -> None:
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "piped content"

        config, errors = parse_command_line_arguments(["-o", "output.md"])

    assert not errors
    assert config.input == "piped content"
    assert config.output_file == "output.md"


# --- defaults ---


def test_defaults_are_applied() -> None:
    config, errors = parse_command_line_arguments(["input.md"])

    assert not errors
    assert config.max_file_size == DEFAULT_MAX_FILE_SIZE
    assert config.max_recursion == DEFAULT_MAX_RECURSION
    assert config.max_memory == DEFAULT_MAX_MEMORY
    assert config.max_embed_size == DEFAULT_MAX_EMBED_SIZE
    assert config.plugin_sequence == DEFAULT_PLUGIN_SEQUENCE
    assert config.is_force_set is False
    assert config.is_dry_run is False


# --- validation errors ---


def test_no_input_no_stdin_returns_error() -> None:
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = True

        config, errors = parse_command_line_arguments([])

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "input" in errors[0].description.lower()


def test_output_file_and_dir_conflict() -> None:
    _, errors = parse_command_line_arguments(["input.md", "-o", "out.md", "-d", "./out"])

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "output" in errors[0].description.lower()
