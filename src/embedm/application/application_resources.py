from types import SimpleNamespace

# TODO move all user facing strings here
str_resources = SimpleNamespace(
    continue_compilation="Continue with compilation (yes/no/always)? [y/N/a]",
    err_cli_file_and_dir_output="cannot specify both --output-file and --output-dir",
    err_cli_no_input="no input provided; pass a file/directory or pipe via stdin",
    err_cli_out_file_and_dir_input="cannot use --output-file with directory input, use --output-dir",
    err_config_no_dir="directory '{directory}' does not exist",
    err_config_dir_exist="'{config_path}' already exists",
    err_config_no_file="config file '{path}' not found",
    err_config_max_file_size_min="'max_file_size' must be >= 1, got {max_file_size}",
    err_config_max_recursion_min="'max_recursion' must be >= 1, got {max_recursion}",
    err_config_max_embed_size_min="'max_embed_size' must be >= 0, got {max_embed_size}",
    err_config_memory_must_exceed_file_size=(
        "'max_memory' ({max_memory}) must be greater than 'max_file_size' ({max_file_size})"
    ),
    err_plan_no_plugin="no plugin registered for directive type '{directive_type}'",
    err_plan_no_plugin_verbose=("no plugin registered for directive type '{directive_type}'. Available: {available}"),
    verbose_hint="Use -v or --verbose for more information.",
)
