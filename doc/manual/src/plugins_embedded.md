# EmbedM Plugins

EmbedM uses a flexible plugin system that allows you to extend its functionality with custom embed types. This guide explains how plugins work and shows you how to create your own.

## Table of Contents

```yaml
type: embed.toc
```

## Overview

Plugins in EmbedM handle specific embed types like `embed.file`, `embed.layout`, or `embed.toc`. The plugin system is based on:

1. **Plugin Interface**: All plugins implement the `EmbedPlugin` abstract base class
2. **Entry Points**: Plugins are discovered automatically via Python entry points
3. **Registry**: A central registry routes embed processing to the correct plugin
4. **Configuration**: Users can enable/disable plugins via `embedm_config.yaml`

### Built-in Plugins

```yaml
type: embed.table
source: ../data/builtin_plugins.json
title: EmbedM Built-in Plugins
```

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

```python
from embedm.plugin import EmbedPlugin
from embedm.phases import ProcessingPhase
from typing import List

class MyPlugin(EmbedPlugin):
    @property
    def name(self) -> str:
        """Unique plugin identifier."""
        return "myplugin"

    @property
    def embed_types(self) -> List[str]:
        """Embed types this plugin handles."""
        return ["mytype"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Processing phases when this plugin runs."""
        return [ProcessingPhase.EMBED]
```

### Required Method

```python
def process(
    self,
    properties: Dict,
    current_file_dir: str,
    processing_stack: Set[str],
    context: Optional[ProcessingContext] = None
) -> str:
    """Process the embed and return content.

    Args:
        properties: YAML properties from the embed block
        current_file_dir: Directory containing the markdown file
        processing_stack: Set of files being processed (cycle detection)
        context: Processing context with limits

    Returns:
        Processed content as string (Markdown or HTML)
    """
    pass
```

### Utility Methods

The base class provides helpful utilities:

```python
# Resolve relative paths
abs_path = self.resolve_path(source, current_file_dir)

# Format error messages
error = self.format_error("File Not Found", f"`{source}` does not exist")

# Check if file exists
error = self.check_file_exists(file_path)
if error:
    return error
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

## Example 2: Real TablePlugin Implementation

Let's look at a real plugin from EmbedM - the TablePlugin that converts CSV and JSON to markdown tables.

### Plugin Structure

```yaml
type: embed.file
source: ../../../src/embedm_plugins/table_plugin.py
region: table_plugin_class
title: TablePlugin Class Definition
```

### JSON Conversion Implementation

The TablePlugin includes a sophisticated method for converting JSON data to markdown tables:

```yaml
type: embed.file
source: ../../../src/embedm_plugins/table_plugin.py
region: json_conversion
line_numbers: text
title: JSON to Markdown Conversion Method
```

### Usage Examples

**CSV Table:**
```yaml
type: embed.table
source: data/users.csv
title: User List
```

**JSON Table:**
```yaml
type: embed.table
source: data/users.json
columns: [name, email, role]
title: Active Users
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
```

The entry point format is:
```
plugin_name = "package.module:ClassName"
```

### Example: EmbedM's Built-in Plugin Entry Points

Here are the actual entry points from EmbedM's `pyproject.toml`:

```yaml
type: embed.file
source: ../../../pyproject.toml
region: plugin_entry_points
title: Built-in Plugin Entry Points
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

### Configuration Options

```yaml
type: embed.layout
orientation: row
gap: 30px
sections:
  - size: 50%
    embed:
      type: embed.file
      source: ../examples/config_all.yaml
      title: "Enable All Plugins (Default)"
  - size: 50%
    embed:
      type: embed.file
      source: ../examples/config_selective.yaml
      title: "Enable Specific Plugins"
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
- [`TablePlugin`](../../src/embedm_plugins/table_plugin.py)
