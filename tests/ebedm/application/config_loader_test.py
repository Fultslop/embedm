from __future__ import annotations

from pathlib import Path

from embedm.application.config_loader import (
    discover_config,
    generate_default_config,
    load_config_file,
)
from embedm.application.configuration import (
    CONFIG_FILE_NAME,
    DEFAULT_MAX_EMBED_SIZE,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_MAX_MEMORY,
    DEFAULT_PLUGIN_SEQUENCE,
    DEFAULT_ROOT_DIRECTIVE_TYPE,
)
from embedm.domain.status_level import StatusLevel

# --- generate_default_config ---


def test_generate_creates_yaml_file(tmp_path: Path) -> None:
    path, errors = generate_default_config(str(tmp_path))

    assert not errors
    assert path == str(tmp_path / CONFIG_FILE_NAME)
    assert (tmp_path / CONFIG_FILE_NAME).is_file()

    content = (tmp_path / CONFIG_FILE_NAME).read_text(encoding="utf-8")
    assert "max_file_size" in content
    assert "max_recursion" in content
    assert "plugin_sequence" in content


def test_generate_existing_file_returns_error(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILE_NAME).write_text("existing", encoding="utf-8")

    _, errors = generate_default_config(str(tmp_path))

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "already exists" in errors[0].description


def test_generate_in_missing_directory_returns_error() -> None:
    _, errors = generate_default_config("./nonexistent_dir_xyz")

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "does not exist" in errors[0].description


# --- load_config_file ---


def test_load_valid_config(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text(
        "max_file_size: 2048\n"
        "max_recursion: 4\n"
        "max_memory: 8192\n"
        "max_embed_size: 1024\n"
        "root_directive_type: custom\n"
        "plugin_sequence:\n"
        "  - my_plugin\n",
        encoding="utf-8",
    )

    config, errors = load_config_file(str(config_file))

    assert not errors
    assert config.max_file_size == 2048
    assert config.max_recursion == 4
    assert config.max_memory == 8192
    assert config.max_embed_size == 1024
    assert config.root_directive_type == "custom"
    assert config.plugin_sequence == ["my_plugin"]


def test_load_partial_config_uses_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text("max_recursion: 3\n", encoding="utf-8")

    config, errors = load_config_file(str(config_file))

    assert not errors
    assert config.max_recursion == 3
    assert config.max_file_size == DEFAULT_MAX_FILE_SIZE
    assert config.max_memory == DEFAULT_MAX_MEMORY
    assert config.max_embed_size == DEFAULT_MAX_EMBED_SIZE
    assert config.root_directive_type == DEFAULT_ROOT_DIRECTIVE_TYPE
    assert config.plugin_sequence == DEFAULT_PLUGIN_SEQUENCE


def test_load_empty_config_uses_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text("", encoding="utf-8")

    config, errors = load_config_file(str(config_file))

    assert not errors
    assert config.max_file_size == DEFAULT_MAX_FILE_SIZE


def test_load_unknown_keys_returns_warning(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text("max_recursion: 3\nunknown_key: value\n", encoding="utf-8")

    config, errors = load_config_file(str(config_file))

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.WARNING
    assert "unknown_key" in errors[0].description
    assert config.max_recursion == 3


def test_load_invalid_type_returns_error(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text("max_recursion: not_a_number\n", encoding="utf-8")

    _, errors = load_config_file(str(config_file))

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "max_recursion" in errors[0].description


def test_load_missing_file_returns_error() -> None:
    _, errors = load_config_file("./nonexistent_config.yaml")

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "not found" in errors[0].description


def test_load_invalid_yaml_returns_error(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text(":\n  - :\n  invalid: [", encoding="utf-8")

    _, errors = load_config_file(str(config_file))

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "parse" in errors[0].description.lower()


def test_load_memory_not_greater_than_file_size_returns_error(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text("max_file_size: 8192\nmax_memory: 4096\n", encoding="utf-8")

    _, errors = load_config_file(str(config_file))

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "max_memory" in errors[0].description
    assert "max_file_size" in errors[0].description


def test_load_non_mapping_returns_error(tmp_path: Path) -> None:
    config_file = tmp_path / CONFIG_FILE_NAME
    config_file.write_text("- item1\n- item2\n", encoding="utf-8")

    _, errors = load_config_file(str(config_file))

    assert len(errors) == 1
    assert errors[0].level == StatusLevel.ERROR
    assert "mapping" in errors[0].description


# --- discover_config ---


def test_discover_finds_config_in_directory(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILE_NAME).write_text("max_recursion: 3\n", encoding="utf-8")
    input_file = tmp_path / "input.md"
    input_file.write_text("content", encoding="utf-8")

    result = discover_config(str(input_file))

    assert result is not None
    assert CONFIG_FILE_NAME in result


def test_discover_returns_none_when_absent(tmp_path: Path) -> None:
    input_file = tmp_path / "input.md"
    input_file.write_text("content", encoding="utf-8")

    result = discover_config(str(input_file))

    assert result is None
