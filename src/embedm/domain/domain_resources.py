from types import SimpleNamespace

str_resources = SimpleNamespace(
    cannot_cast_directive_option="Cannot cast option '{name}' to {cast_name} (Value: '{value}')",
    config_memory_must_exceed_file_size=(
        "'max_memory' ({max_memory}) must be greater than 'max_file_size' ({max_file_size})"
    ),
)
