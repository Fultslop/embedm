# Query-Path Plugin

version 0.9.6

The query-path plugin extracts and embeds a value from a structured data file using a dot-notation path. It supports JSON, YAML, TOML, and XML sources. Without a path the full file is embedded as a fenced code block; with a path the resolved value is rendered inline or as a nested structure.

  - [Basic Usage](#basic-usage)
  - [Path Expressions](#path-expressions)
    - [Dot notation](#dot-notation)
    - [Array indexing](#array-indexing)
    - [Backtick escaping](#backtick-escaping)
  - [Format Strings](#format-strings)
  - [Extracting Structures](#extracting-structures)
  - [Supported Formats](#supported-formats)
    - [JSON](#json)
    - [YAML](#yaml)
    - [TOML](#toml)
    - [XML](#xml)
  - [Architecture](#architecture)
  - [Adding a New Format](#adding-a-new-format)

## Basic Usage

Embed a data file with `type: query-path` and a `source` path. Without a `path` option the complete file is rendered as a fenced code block:

```yaml
type: query-path
source: ./example_data.json
```

```json
{
    "project": {
        "name": "my-app",
        "version": "1.2.0",
        "tags": ["backend", "api", "stable"]
    },
    "build": {
        "target": "production",
        "minify": true
    }
}
```

Supply a `path` to extract a single value. Scalar results (strings, numbers, booleans) are rendered as inline text:

```yaml
type: query-path
source: ./example_data.json
path: project.name
```

my-app

## Path Expressions

### Dot notation

Use dots to descend through nested keys. Each segment is resolved against the current node in the parsed tree:

```yaml
type: query-path
source: ./example_data.json
path: build.target
```

production

### Array indexing

Use an integer segment to index into a list. Indices are zero-based:

```yaml
type: query-path
source: ./example_data.json
path: project.tags.0
```

backend

### Backtick escaping

Wrap a segment in backticks to use it as a literal key lookup, bypassing dot-splitting. This is required when a key contains a dot, or when querying XML nodes named `value` or `attributes` (which are reserved keys in the XML normalisation — see [Supported Formats](#supported-formats)):

```
path: "config.`value`.child"
```

## Format Strings

Add `format` to interpolate a scalar result into a template string. The placeholder `{value}` is replaced with the resolved value. `format` requires a `path` and is only valid for scalar values.

```yaml
type: query-path
source: ./example_data.json
path: project.version
format: "Released as **version {value}**"
```

Released as **version 1.2.0**

## Extracting Structures

When the resolved value is a dict or list, it is rendered as a YAML fenced code block:

```yaml
type: query-path
source: ./example_data.json
path: project.tags
```

```yaml
- backend
- api
- stable
```

Extracting a nested object works the same way:

```yaml
type: query-path
source: ./example_data.json
path: project
```

```yaml
name: my-app
tags:
- backend
- api
- stable
version: 1.2.0
```

## Supported Formats

### JSON

Standard JSON files. All JSON types map directly to Python primitives.

```yaml
type: query-path
source: ./example_data.json
path: build.minify
```

true

Boolean values render as `true` or `false`; null renders as `null`.

### YAML

`.yaml` and `.yml` files are supported. The parsed structure and path syntax are identical to JSON:

```yaml
type: query-path
source: ./example_data.yaml
path: project.tags.1
```

api

### TOML

TOML files are fully supported. The `pyproject.toml` at the repository root is a common use case:

```yaml
type: query-path
source: ../../../pyproject.toml
path: project.name
```

embedm

### XML

XML files are normalised into a Python dict before path resolution. The normalisation rules are:

- **Element text content** is stored under the reserved key `value`.
- **Element attributes** are stored under the reserved key `attributes`.
- **Multiple child elements** with the same tag are stored as a list.
- **Children whose tag is a reserved key** (`value` or `attributes`) are stored with the tag wrapped in backticks.

The root tag is included as the first key, so paths always start with the root element name.

Accessing an attribute:

```yaml
type: query-path
source: ./example_data.xml
path: config.project.attributes.name
```

my-app

Accessing text content via the `value` key:

```yaml
type: query-path
source: ./example_data.xml
path: config.project.description.value
```

A backend API service

## Architecture

The plugin processes each directive in three stages:

**1. Normalize** — The source file is read from the cache and parsed into a uniform Python tree by a format-specific normalizer (`query_path_normalize_<format>.py`). Each normalizer exposes a single `normalize(content: str) -> Any` function.

**2. Resolve** — `engine.parse_path` splits the `path` string into segments using the backtick-aware regex. `engine.resolve` walks the tree segment by segment, dispatching to dict key lookup or integer list indexing as appropriate. A missing key or out-of-range index raises an error at plan time.

**3. Render** — `QueryPathTransformer` converts the resolved value to a string:
- No path: raw file content as a fenced code block (using the file extension as language tag).
- Scalar (str, int, float, bool, None): inline text, optionally wrapped in a `format` template.
- Dict or list: YAML dump in a fenced code block.

## Adding a New Format

To add support for a new file format:

1. Create `src/embedm_plugins/query_path_normalize_<format>.py` with a `normalize(content: str) -> Any` function that parses the file content and returns a Python dict or list.
2. In `query_path_plugin.py`:
   - Add the extension to `_SUPPORTED_EXTENSIONS`.
   - Add an entry to `_EXT_TO_LANG_TAG` mapping the extension to its fenced-block language tag.
   - Add a branch in `_parse()` calling the new normalizer.
   - Add a parse error message resource to `query_path_resources.py` and a corresponding branch in `_parse_error_message()`.
