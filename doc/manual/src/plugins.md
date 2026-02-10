# EmbedM Plugins

EmbedM uses a flexible plugin system that allows you to extend its functionality with custom embed types. This guide explains how plugins work and shows you how to create your own.

## Table of Contents

```yaml embedm
type: toc
```

## Overview

Plugins in EmbedM handle specific embed types like `embed.file`, `embed.layout`, or `embed.toc`. The plugin system is based on:

1. **Plugin Interface**: All plugins implement the `EmbedPlugin` abstract base class
2. **Entry Points**: Plugins are discovered automatically via Python entry points
3. **Registry**: A central registry routes embed processing to the correct plugin
4. **Configuration**: Users can enable/disable plugins via `embedm_config.yaml`

### Built-in Plugins

EmbedM includes three built-in plugins:

- **FilePlugin**: Embeds files and code snippets (`embed.file`)
- **LayoutPlugin**: Creates multi-column/row layouts (`embed.layout`)
- **TOCPlugin**: Generates table of contents (`embed.toc`)

## How Plugins Work

When EmbedM processes a markdown file:

1. **Discovery**: Plugins are discovered via entry points defined in `pyproject.toml`
2. **Registration**: Discovered plugins are registered in the plugin registry
3. **Processing**: When an embed block is encountered, the registry dispatches to the appropriate plugin
4. **Phases**: Plugins can run in different processing phases (EMBED, POST_PROCESS)

```
User's Markdown → Parser → Registry Dispatcher → Plugin.process() → Output
```

## The EmbedPlugin Interface

All plugins must inherit from `embedm.plugin.EmbedPlugin` and implement these methods:

### Required Properties

```yaml embedm
type: file
source: ../../../src/embedm/plugin.py
region: abstract_properties
```

### Required Method

```yaml embedm
type: file
source: ../../../src/embedm/plugin.py
region: process_method
```

### Utility Methods

The base class provides helpful utilities:

```yaml embedm
type: file
source: ../../../src/embedm/plugin.py
region: utility_methods
```

## Processing Phases

EmbedM has two processing phases:

1. **EMBED Phase**: Main processing phase where most plugins run
   - Embeds files, creates layouts, etc.
   - Runs first

2. **POST_PROCESS Phase**: Second pass for content-dependent operations
   - Generates TOC from final document content
   - Runs after all EMBED phase processing

Plugins can run in one or both phases by returning the appropriate list from the `phases` property.

## Example 1: Simple Quote Plugin

Let's create a plugin that embeds inspirational quotes:

```python
# quote_plugin.py
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from typing import Dict, Set, Optional, List
from embedm.resolver import ProcessingContext

class QuotePlugin(EmbedPlugin):
    """Plugin that displays quotes in a styled callout box."""

    @property
    def name(self) -> str:
        return "quote"

    @property
    def embed_types(self) -> List[str]:
        return ["quote"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        return [ProcessingPhase.EMBED]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process quote embed."""

        # Extract properties
        text = properties.get('text')
        author = properties.get('author')
        source = properties.get('source')

        # Validate required fields
        if not text:
            return self.format_error("Quote Error", "'text' property is required")

        # Build quote content
        quote_lines = ["> [!NOTE]"]
        quote_lines.append(f"> {text}")

        if author:
            attribution = f"— {author}"
            if source:
                attribution += f", *{source}*"
            quote_lines.append(f"> ")
            quote_lines.append(f"> {attribution}")

        return '\n'.join(quote_lines)
```

### Usage

In your markdown:

```yaml
type: embed.quote
text: "The only way to do great work is to love what you do."
author: Steve Jobs
```

### Output

> [!NOTE]
> The only way to do great work is to love what you do.
>
> — Steve Jobs

## Example 2: Metadata Plugin

A plugin that embeds project metadata from `pyproject.toml` as a markdown table:

```python
# metadata_plugin.py
import tomllib
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from typing import Dict, Set, Optional, List
from embedm.resolver import ProcessingContext

class MetadataPlugin(EmbedPlugin):
    """Plugin that embeds project metadata from pyproject.toml."""

    @property
    def name(self) -> str:
        return "metadata"

    @property
    def embed_types(self) -> List[str]:
        return ["metadata"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        return [ProcessingPhase.EMBED]

    @property
    def valid_properties(self) -> List[str]:
        return ["source", "fields"]

    def process(
        self,
        properties: Dict,
        current_file_dir: str,
        processing_stack: Set[str],
        context: Optional[ProcessingContext] = None
    ) -> str:
        """Process metadata embed."""

        # Get source file
        source = properties.get('source')
        if not source:
            return self.format_error("Metadata Error", "'source' property is required")

        # Resolve path and check existence
        file_path = self.resolve_path(source, current_file_dir)
        error = self.check_file_exists(file_path)
        if error:
            return error

        # Read and parse TOML
        try:
            with open(file_path, 'rb') as f:
                data = tomllib.load(f)
        except Exception as e:
            return self.format_error("Metadata Error", f"Could not parse TOML: {e}")

        # Extract project metadata
        project = data.get('project', {})
        fields = properties.get('fields', list(project.keys()))

        # Build markdown table
        lines = ['| Field | Value |', '| --- | --- |']
        for field in fields:
            value = project.get(field, '*not set*')
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            lines.append(f'| {field} | {value} |')

        return '\n'.join(lines)
```

### Usage

```yaml
type: metadata
source: pyproject.toml
fields: [name, version, description]
```

### Output

| Field | Value |
| --- | --- |
| name | embedm |
| version | 0.4.0 |
| description | A Python tool for embedding files... |

## Registering Your Plugin

To make your plugin discoverable by EmbedM, register it as a Python entry point.

### Step 1: Package Your Plugin

Create a Python package structure:

```
my-embedm-plugin/
├── pyproject.toml
├── src/
│   └── embedm_myplugin/
│       ├── __init__.py
│       ├── quote_plugin.py
│       └── metadata_plugin.py
```

### Step 2: Define Entry Point

In `pyproject.toml`:

```toml
[project]
name = "embedm-myplugin"
version = "0.1.0"
dependencies = ["embedm>=0.4.0"]

[project.entry-points."embedm.plugins"]
quote = "embedm_myplugin.quote_plugin:QuotePlugin"
metadata = "embedm_myplugin.metadata_plugin:MetadataPlugin"
```

The entry point format is:
```
plugin_name = "package.module:ClassName"
```

For reference, here are EmbedM's built-in plugin entry points:

```yaml embedm
type: file
source: ../../../pyproject.toml
region: entry_points
```

### Step 3: Install Your Plugin

```bash
# Install in development mode
pip install -e my-embedm-plugin

# Or install from package
pip install embedm-myplugin
```

### Step 4: Verify Discovery

Run EmbedM with verbose output to see discovered plugins:

```bash
embedm --verbose input.md
```

## Configuring Plugins

Control which plugins are enabled via `embedm_config.yaml`.

### Enable All Plugins (Default)

```yaml
plugins: "*"
```

### Enable Specific Plugins

```yaml
plugins:
  - file
  - toc
  - quote
  - metadata
```

### Configuration Precedence

1. **Config file**: `embedm_config.yaml` in source directory
2. **Default**: All discovered plugins enabled

When processing a directory, EmbedM looks for `embedm_config.yaml` and respects the plugin configuration.

## Development Tips

### 1. Error Handling

Always return error strings, don't raise exceptions:

```python
# Good
if not source:
    return self.format_error("Error", "message")

# Bad - don't do this
if not source:
    raise ValueError("message")
```

### 2. Use Utility Methods

The base class provides helpers:

```python
# Path resolution
path = self.resolve_path(source, current_file_dir)

# File existence check
error = self.check_file_exists(path)
if error:
    return error

# Consistent error formatting
return self.format_error("Category", "Message")
```

### 3. Handle Context and Limits

Check limits when processing large files:

```python
if context and context.limits:
    limit = context.limits.max_file_size
    if limit > 0 and file_size > limit:
        return self.format_error(
            "Limit Exceeded",
            f"File size {file_size} exceeds limit {limit}"
        )
```

### 4. Cycle Detection

Use `processing_stack` to detect circular dependencies:

```python
if target_path in processing_stack:
    return self.format_error(
        "Circular Dependency",
        f"Recursive embed detected: {target_path}"
    )

# Add to stack before processing
new_stack = processing_stack | {target_path}
# Pass new_stack to nested embeds
```

### 5. Multi-Phase Plugins

If your plugin needs document content, run in POST_PROCESS phase:

```python
@property
def phases(self) -> List[ProcessingPhase]:
    return [ProcessingPhase.POST_PROCESS]
```

### 6. Testing Your Plugin

Write comprehensive tests:

```python
import pytest
from my_plugin import QuotePlugin

def test_quote_plugin_basic():
    plugin = QuotePlugin()

    properties = {
        'text': 'Test quote',
        'author': 'Test Author'
    }

    result = plugin.process(properties, '/tmp', set())

    assert 'Test quote' in result
    assert 'Test Author' in result

def test_quote_plugin_missing_text():
    plugin = QuotePlugin()
    result = plugin.process({}, '/tmp', set())
    assert '[!CAUTION]' in result
    assert "'text' property is required" in result
```

### 7. Documentation

Document your plugin's YAML schema:

```python
class MyPlugin(EmbedPlugin):
    """My custom plugin.

    YAML Schema:
        type: embed.mytype
        source: str (required) - Path to source file
        format: str (optional) - Output format (default: 'auto')
        title: str (optional) - Title for output

    Example:
        ```yaml
        type: embed.mytype
        source: data.txt
        format: code
        title: "My Data"
        ```
    """
```

## Summary

Creating EmbedM plugins is straightforward:

1. **Implement** the `EmbedPlugin` interface
2. **Define** properties: name, embed_types, phases
3. **Implement** the `process()` method
4. **Register** via entry points in `pyproject.toml`
5. **Install** your plugin package
6. **Configure** in `embedm_config.yaml` (optional)

The plugin system gives you full control over how embed types are processed while maintaining safety and consistency with EmbedM's validation pipeline.

For more examples, check out the built-in plugins:
- [`FilePlugin`](../../src/embedm_plugins/file_plugin.py)
- [`LayoutPlugin`](../../src/embedm_plugins/layout_plugin.py)
- [`TOCPlugin`](../../src/embedm_plugins/toc_plugin.py)
