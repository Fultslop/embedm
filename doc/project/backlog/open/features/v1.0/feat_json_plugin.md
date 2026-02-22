FEATURE: JSON / YAML plugin
========================================
Draft
Release v1.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

A plugin that extracts and embeds a specific value from a JSON or YAML file using a dot-notation key path. Output is plain inline text.

The primary use case is keeping version numbers, metadata, and configuration values in a single source file and embedding them into documentation automatically — eliminating the manual synchronisation problem.

Directive definition:

```yaml embedm
type: json
source: ./package.json
path: version
```

```yaml embedm
type: yaml
source: ./pyproject.toml
path: project.version
```

### Behaviour

- `source` is required; there is no current-document mode.
- `path` is a dot-separated key sequence into the parsed structure (e.g. `project.version`, `dependencies.react`).
- If `path` is omitted, the entire document is embedded as a fenced code block.
- If a path segment is a list index, integer notation is supported (`servers.0.host`).
- If the resolved value is a scalar (string, number, bool), it is output as plain inline text with no trailing newline — so it can be embedded mid-sentence.
- If the resolved value is a dict or list, it is formatted as a fenced `yaml` code block.
- Path not found → error caution block.

### Architecture

- Single plugin handles both `.json` and `.yaml`/`.yml` — file extension determines the parser.
- Uses `json` stdlib and `PyYAML` (already a dependency).
- `type: json` is the directive type; `type: yaml` is an alias handled by the same plugin class.
- Plugin sequence: runs after `file` (or as its own pass — TBD based on whether source files can themselves be embedded).

## Acceptance criteria

- Scalar value at a given path is embedded as plain text (no trailing newline, embeddable inline)
- Nested path notation (`a.b.c`) resolves correctly
- Integer index in path resolves list elements
- Full document embed (no `path`) outputs a fenced code block
- `.json`, `.yaml`, `.yml` extensions all supported
- Invalid path → error caution block
- Invalid JSON/YAML → error caution block
- Unit and integration tests included
- Regression example included

## Comments

`22/02/2026 FS/Claude:` Killer use case: embedding `version` from `pyproject.toml` or `package.json` into a README or changelog. Also useful for embedding API config (base URLs, environment names) into documentation. Shares no infrastructure with table plugin — data loading is separate and simpler.
