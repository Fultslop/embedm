from types import SimpleNamespace

# TODO move all user facing strings here
str_resources = SimpleNamespace(
    continue_compilation="Continue with compilation (yes/no/always/exit)? [y/N/a/x]",
    err_cli_file_and_dir_output="cannot specify both --output-file and --output-dir",
    err_cli_no_input="no input provided; pass a file/directory or pipe via stdin",
    err_cli_out_file_and_dir_input="cannot use --output-file with directory input, use --output-dir",
    err_cli_verify_and_dry_run="--verify and --dry-run are mutually exclusive",
    err_cli_verify_requires_output="--verify requires --output-file or --output-dir",
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
    verbose_hint="Use -v 3 or --verbose 3 for more information.",
    err_cli_invalid_verbosity="verbosity level must be 0-3, got {level}",
    err_fatal_plugins_cannot_start=(
        "Embedm cannot start, please fix these issues first or disable the plugins in 'embedm-config.yaml'"
    ),
    warn_unresolved_plugin_sequence=(
        "plugin_sequence entry '{module}' has no matching installed entry point — plugin will not load"
    ),
)
