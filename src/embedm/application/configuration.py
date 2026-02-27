from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any


class InputMode(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    STDIN = "stdin"


DEFAULT_MAX_FILE_SIZE = 1_048_576  # 1 MB
DEFAULT_MAX_RECURSION = 8
DEFAULT_MAX_MEMORY = 104_857_600  # 100 MB
DEFAULT_MAX_EMBED_SIZE = 524_288  # 512 KB
DEFAULT_ROOT_DIRECTIVE_TYPE = "file"
DEFAULT_LINE_ENDINGS = "lf"
CONFIG_FILE_NAME = "embedm-config.yaml"

# include standard embedm plugins
DEFAULT_PLUGIN_SEQUENCE = [
    # plugins using source
    "embedm_plugins.file_plugin",
    "embedm_plugins.query_path_plugin",
    "embedm_plugins.table_plugin",
    # plugins having no dependencies
    "embedm_plugins.hello_world_plugin",
    # plugins requiring the document to be complete(ish)
    "embedm_plugins.synopsis_plugin",
    "embedm_plugins.recall_plugin",
    "embedm_plugins.toc_plugin",
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

    # directive type used for the root plan node
    root_directive_type: str = DEFAULT_ROOT_DIRECTIVE_TYPE

    # order in which plugins must be executed during the compile stage
    plugin_sequence: list[str] = field(default_factory=lambda: list(DEFAULT_PLUGIN_SEQUENCE))

    # if set, the user will not be prompted to continue on errors (errors still shown)
    is_accept_all: bool = False

    # will only run, does not save any files
    is_dry_run: bool = False

    # if set, compile and compare against existing files but do not write
    is_verify: bool = False

    # line endings applied to output files: "lf" (default) or "crlf"
    line_endings: str = DEFAULT_LINE_ENDINGS

    # path to the config file (from --config or auto-discovered)
    config_file: str | None = None

    # path for --init output (generate config file and exit)
    init_path: str | None = None

    # if set, print plugin list and diagnostics then exit
    plugin_list: bool = False

    # verbosity level: 0 silent, 1 minimal, 2 default, 3 verbose
    verbosity: int = 2

    # per-plugin configuration keyed by plugin module name
    plugin_configuration: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def merge(cls, cli_config: Configuration, file_config: Configuration, config_path: str) -> Configuration:
        """Return a new Configuration combining file config values with CLI-specific overrides.

        file_config provides all user-configurable settings (limits, plugins, line_endings, …).
        CLI-only fields (input, output targets, run-mode flags) are taken from cli_config.
        Adding a new file-configurable field only requires updating the dataclass — not this method.
        """
        return replace(
            file_config,
            input_mode=cli_config.input_mode,
            input=cli_config.input,
            output_file=cli_config.output_file,
            output_directory=cli_config.output_directory,
            is_accept_all=cli_config.is_accept_all,
            is_dry_run=cli_config.is_dry_run,
            is_verify=cli_config.is_verify,
            verbosity=cli_config.verbosity,
            init_path=cli_config.init_path,
            plugin_list=cli_config.plugin_list,
            config_file=config_path,
        )
