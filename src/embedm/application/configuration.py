from typing import Any


class Configuration:
    # list or markdown files to process
    file_list: list[str]

    # default extension added to the compiled files if no target
    # directory is set, will be used as file_name.ext.file_ext
    default_file_extension: str

    # output directory
    target_directory: str

    # max file size that can be loaded
    max_file_size: int

    # max depth of recursion
    max_recursion: int

    # max memory available to the file cache
    max_memory: int

    # max number of characters in a resolved embed block
    max_embed_size: int

    # order in which plugins must be executed during the compile stage
    plugin_sequence: Any | None

    # if set, warnings and errors will be skipped during the validation
    # step unless the errors affect the limits
    is_force_set: bool

    # will only run, does not save any files
    is_dry_run: bool
