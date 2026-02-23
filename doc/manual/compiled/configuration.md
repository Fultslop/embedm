# Configuration

version 0.6.1

embedm is configured via a YAML file named `embedm-config.yaml`. Settings in this file control file size limits, recursion depth, output format, and which plugins are loaded.

  - [File Discovery](#file-discovery)
  - [CLI vs Config File](#cli-vs-config-file)
  - [Properties](#properties)
    - [max_file_size](#max-file-size)
    - [max_recursion](#max-recursion)
    - [max_memory](#max-memory)
    - [max_embed_size](#max-embed-size)
    - [line_endings](#line-endings)
    - [root_directive_type](#root-directive-type)
    - [plugin_sequence](#plugin-sequence)
    - [plugin_configuration](#plugin-configuration)
  - [Complete Example](#complete-example)

## File Discovery

embedm looks for `embedm-config.yaml` in the same directory as the input file. If found, it is loaded automatically. Use `-c` to specify an explicit path:

```
embedm content.md -c path/to/embedm-config.yaml
```

To generate a default config file in the current directory:

```
embedm --init
```

## CLI vs Config File

CLI flags always take precedence. Input paths, output targets, and run-mode flags (`--dry-run`, `--verify`, `--accept-all`, `--verbose`) are CLI-only and cannot be set in the config file. All other settings are config-file properties that the CLI cannot override.

## Properties

### max_file_size

Maximum size in bytes of any single source file the cache will load. Files exceeding this limit produce an error and are not embedded.

```yaml
max_file_size: 1048576   # default: 1 MB
```

### max_recursion

Maximum depth of nested embeds. A file embedded at depth 8 (the default) will not have its own directives compiled.

```yaml
max_recursion: 8   # default
```

### max_memory

Total memory budget in bytes for the file cache. When the cache would exceed this limit, least-recently-used entries are evicted. Must be greater than `max_file_size`.

```yaml
max_memory: 104857600   # default: 100 MB
```

### max_embed_size

Maximum size in bytes of any single compiled embed result. Results exceeding this limit are replaced with an inline error note. Set to `0` to disable the check.

```yaml
max_embed_size: 524288   # default: 512 KB
max_embed_size: 0        # unlimited
```

### line_endings

Line-ending style applied to all output files. Accepted values: `lf` (Unix) and `crlf` (Windows).

```yaml
line_endings: lf     # default
line_endings: crlf
```

### root_directive_type

Directive type used for the root plan node of each compiled document. Changing this substitutes a different plugin as the document compiler. The default `file` value uses the file plugin, which handles markdown compilation recursively.

```yaml
root_directive_type: file   # default
```

This is an advanced setting; leave it at the default unless you are building a custom compilation pipeline.

### plugin_sequence

Ordered list of plugin module paths to load. Plugins are loaded in this order and compiled in the same order (one full pass per plugin, left to right). Plugins discovered via entry-points but absent from this list are not loaded.

```yaml
plugin_sequence:
  - embedm_plugins.file_plugin
  - embedm_plugins.query_path_plugin
  - embedm_plugins.table_plugin
  - embedm_plugins.hello_world_plugin
  - embedm_plugins.synopsis_plugin
  - embedm_plugins.recall_plugin
  - embedm_plugins.toc_plugin
```

Order matters: plugins that read the compiled document (`toc_plugin`, `synopsis_plugin`, and `recall_plugin`) must appear after the plugins that produce the content they scan.

### plugin_configuration

Per-plugin settings, keyed by plugin module path. Each value is a mapping passed to that plugin during validation and transformation. Supported keys are declared by each plugin's `get_plugin_config_schema()` method.

```yaml
plugin_configuration:
  embedm_plugins.file_plugin:
    region_start: "// region:{tag}"
    region_end: "// endregion:{tag}"
```

An unknown module key produces a warning. An unknown settings key produces a warning at verbosity 3 and is silently ignored otherwise. An incorrect value type produces an error.

## Complete Example

```yaml
max_file_size: 2097152      # 2 MB
max_recursion: 12
max_memory: 209715200       # 200 MB
max_embed_size: 0           # unlimited
line_endings: lf

plugin_sequence:
  - embedm_plugins.file_plugin
  - embedm_plugins.query_path_plugin
  - embedm_plugins.table_plugin
  - embedm_plugins.synopsis_plugin
  - embedm_plugins.recall_plugin
  - embedm_plugins.toc_plugin

plugin_configuration:
  embedm_plugins.file_plugin:
    region_start: "// region:{tag}"
    region_end: "// endregion:{tag}"
```
