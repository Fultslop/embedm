from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InputMode(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    STDIN = "stdin"


DEFAULT_MAX_FILE_SIZE = 1_048_576  # 1 MB
DEFAULT_MAX_RECURSION = 8
DEFAULT_MAX_MEMORY = 104_857_600  # 100 MB
DEFAULT_MAX_EMBED_SIZE = 524_288  # 512 KB
DEFAULT_PLUGIN_SEQUENCE = [
    "embedm_plugins.embedm_file_plugin",
    "embedm_plugins.hello_world_plugin",
]


@dataclass
class Configuration:
    input_mode: InputMode = InputMode.FILE

    # text, file path or directory path
    input: str = ""

    # output file name, if both this and the output directory are none
    # output will be written to std.out
    output_file: str | None = None

    # output directory, if both this and the output file are none
    # output will be written to std.out
    output_directory: str | None = None

    # max file size that can be loaded
    max_file_size: int = DEFAULT_MAX_FILE_SIZE

    # max depth of recursion
    max_recursion: int = DEFAULT_MAX_RECURSION

    # max memory available to the file cache
    max_memory: int = DEFAULT_MAX_MEMORY

    # max number of characters in a resolved embed block
    max_embed_size: int = DEFAULT_MAX_EMBED_SIZE

    # order in which plugins must be executed during the compile stage
    plugin_sequence: list[str] = field(default_factory=lambda: list(DEFAULT_PLUGIN_SEQUENCE))

    # if set, warnings and errors will be skipped during the validation
    # step unless the errors affect the limits
    is_force_set: bool = False

    # will only run, does not save any files
    is_dry_run: bool = False
