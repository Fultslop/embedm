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

## Example 2: JSON Data Plugin

A more complex plugin that embeds JSON files as formatted tables:

```python
# json_plugin.py
import json
import os
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from typing import Dict, Set, Optional, List
from embedm.resolver import ProcessingContext

class JSONPlugin(EmbedPlugin):
    """Plugin that embeds JSON files as markdown tables or code blocks."""

    @property
    def name(self) -> str:
        return "json"

    @property
    def embed_types(self) -> List[str]:
        return ["json"]

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
        """Process JSON embed."""

        # Get source file
        source = properties.get('source')
        if not source:
            return self.format_error("JSON Error", "'source' property is required")

        # Resolve path and check existence
        file_path = self.resolve_path(source, current_file_dir)
        error = self.check_file_exists(file_path)
        if error:
            return error

        # Read and parse JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return self.format_error("JSON Parse Error", f"Invalid JSON: {str(e)}")
        except Exception as e:
            return self.format_error("JSON Error", f"Could not read file: {str(e)}")

        # Get display format
        format_type = properties.get('format', 'table')

        if format_type == 'table':
            return self._format_as_table(data, properties)
        elif format_type == 'code':
            return self._format_as_code(data, properties)
        else:
            return self.format_error("JSON Error", f"Unknown format: '{format_type}'")

    def _format_as_table(self, data: any, properties: Dict) -> str:
        """Format JSON data as markdown table."""

        # Handle list of objects (typical JSON structure)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Get columns from first object or from properties
            columns = properties.get('columns')
            if not columns:
                columns = list(data[0].keys())

            # Build table header
            lines = ['| ' + ' | '.join(columns) + ' |']
            lines.append('| ' + ' | '.join(['---'] * len(columns)) + ' |')

            # Build table rows
            for item in data:
                row = []
                for col in columns:
                    value = item.get(col, '')
                    # Escape pipes in values
                    value_str = str(value).replace('|', '\\|')
                    row.append(value_str)
                lines.append('| ' + ' | '.join(row) + ' |')

            return '\n'.join(lines)

        # For other structures, fall back to key-value table
        if isinstance(data, dict):
            lines = ['| Key | Value |']
            lines.append('| --- | --- |')
            for key, value in data.items():
                value_str = str(value).replace('|', '\\|')
                lines.append(f'| {key} | {value_str} |')
            return '\n'.join(lines)

        return self.format_error("JSON Error", "Data must be a list or dictionary for table format")

    def _format_as_code(self, data: any, properties: Dict) -> str:
        """Format JSON as pretty-printed code block."""

        indent = properties.get('indent', 2)
        json_str = json.dumps(data, indent=indent, ensure_ascii=False)

        return f"```json\n{json_str}\n```"
```

### Usage

**Table format:**

```yaml
type: embed.json
source: data/users.json
format: table
columns: [name, email, role]
```

**Code format:**

```yaml
type: embed.json
source: config.json
format: code
indent: 4
```

### Output

**Table format (for `[{"name": "Alice", "email": "alice@example.com", "role": "Admin"}]`):**

| name | email | role |
| --- | --- | --- |
| Alice | alice@example.com | Admin |

**Code format:**

```json
{
  "theme": "dark",
  "timeout": 30
}
```

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
│       └── quote_plugin.py
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
json = "embedm_myplugin.json_plugin:JSONPlugin"
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
  - json
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
