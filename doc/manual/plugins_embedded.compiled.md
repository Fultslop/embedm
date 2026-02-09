# EmbedM Plugins

EmbedM uses a flexible plugin system that allows you to extend its functionality with custom embed types. This guide explains how plugins work and shows you how to create your own.

## Table of Contents

- [Overview](#overview)
  - [Built-in Plugins](#built-in-plugins)
- [How Plugins Work](#how-plugins-work)
- [The EmbedPlugin Interface](#the-embedplugin-interface)
  - [Required Properties](#required-properties)
  - [Required Method](#required-method)
  - [Utility Methods](#utility-methods)
- [Processing Phases](#processing-phases)
- [Example 1: Simple Quote Plugin](#example-1-simple-quote-plugin)
  - [Usage](#usage)
  - [Output](#output)
- [Example 2: Real TablePlugin Implementation](#example-2-real-tableplugin-implementation)
  - [Plugin Structure](#plugin-structure)
  - [JSON Conversion Implementation](#json-conversion-implementation)
  - [Usage Examples](#usage-examples)
- [Registering Your Plugin](#registering-your-plugin)
  - [Step 1: Package Your Plugin](#step-1-package-your-plugin)
  - [Step 2: Define Entry Point](#step-2-define-entry-point)
  - [Example: EmbedM's Built-in Plugin Entry Points](#example-embedms-built-in-plugin-entry-points)
  - [Step 3: Install Your Plugin](#step-3-install-your-plugin)
  - [Step 4: Verify Discovery](#step-4-verify-discovery)
- [Configuring Plugins](#configuring-plugins)
  - [Configuration Options](#configuration-options)
  - [Configuration Precedence](#configuration-precedence)
- [Development Tips](#development-tips)
  - [1. Error Handling](#1-error-handling)
  - [2. Use Utility Methods](#2-use-utility-methods)
  - [3. Handle Context and Limits](#3-handle-context-and-limits)
  - [4. Cycle Detection](#4-cycle-detection)
  - [5. Multi-Phase Plugins](#5-multi-phase-plugins)
  - [6. Testing Your Plugin](#6-testing-your-plugin)
  - [7. Documentation](#7-documentation)
- [Summary](#summary)

## Overview

Plugins in EmbedM handle specific embed types like `embed.file`, `embed.layout`, or `embed.toc`. The plugin system is based on:

1. **Plugin Interface**: All plugins implement the `EmbedPlugin` abstract base class
2. **Entry Points**: Plugins are discovered automatically via Python entry points
3. **Registry**: A central registry routes embed processing to the correct plugin
4. **Configuration**: Users can enable/disable plugins via `embedm_config.yaml`

### Built-in Plugins

**EmbedM Built-in Plugins**

| name | embed_type | description |
| --- | --- | --- |
| FilePlugin | embed.file | Embeds files and code snippets with line numbers and regions |
| LayoutPlugin | embed.layout | Creates multi-column/row flexbox layouts |
| TOCPlugin | embed.toc | Generates table of contents from markdown headings |
| TablePlugin | embed.table | Converts CSV/JSON data to markdown tables |

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

> [!CAUTION]
> **Embed Error:** Unknown embed type: `quote`

### Output

> [!NOTE]
> The only way to do great work is to love what you do.
>
> — Steve Jobs

## Example 2: Real TablePlugin Implementation

Let's look at a real plugin from EmbedM - the TablePlugin that converts CSV and JSON to markdown tables.

### Plugin Structure

**TablePlugin Class Definition**

```py
class TablePlugin(EmbedPlugin):
    """Plugin that handles table embeds from CSV, JSON, and other tabular formats.

    Handles embed types:
    - embed.table: Convert CSV/JSON/TSV/etc. to markdown tables
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "table"

    @property
    def embed_types(self) -> List[str]:
        """Embed types handled by this plugin."""
        return ["table"]

    @property
    def phases(self) -> List[ProcessingPhase]:
        """Processing phases when this plugin runs."""
        return [ProcessingPhase.EMBED]
```

### JSON Conversion Implementation

The TablePlugin includes a sophisticated method for converting JSON data to markdown tables:

**JSON to Markdown Conversion Method**

```py
155 | def _json_to_markdown_table(self, data: Any, columns: Optional[List[str]] = None) -> str:
156 |     """Convert JSON data to markdown table.
157 | 
158 |     Args:
159 |         data: Parsed JSON data (array of objects, single object, or dict)
160 |         columns: Optional list of column names to include (in order)
161 | 
162 |     Returns:
163 |         Markdown table string or error message
164 |     """
165 |     # Case 1: Array of objects (most common)
166 |     if isinstance(data, list):
167 |         if not data:
168 |             return "> [!CAUTION]\n> **Table Error:** JSON array is empty"
169 | 
170 |         # Check if all items are objects
171 |         if not all(isinstance(item, dict) for item in data):
172 |             return "> [!CAUTION]\n> **Table Error:** JSON array must contain objects for table conversion"
173 | 
174 |         # Determine columns
175 |         if columns:
176 |             # Use specified columns
177 |             cols = columns
178 |         else:
179 |             # Use keys from first object
180 |             cols = list(data[0].keys())
181 | 
182 |         # Build table header
183 |         lines = ['| ' + ' | '.join(cols) + ' |']
184 |         lines.append('| ' + ' | '.join(['---'] * len(cols)) + ' |')
185 | 
186 |         # Build table rows
187 |         for item in data:
188 |             row = []
189 |             for col in cols:
190 |                 value = item.get(col, '')
191 |                 # Convert value to string and escape pipes
192 |                 if isinstance(value, bool):
193 |                     value_str = 'true' if value else 'false'
194 |                 elif value is None:
195 |                     value_str = ''
196 |                 else:
197 |                     value_str = str(value)
198 |                 value_str = value_str.replace('|', '\\|').replace('\n', ' ')
199 |                 row.append(value_str)
200 |             lines.append('| ' + ' | '.join(row) + ' |')
201 | 
202 |         return '\n'.join(lines)
203 | 
204 |     # Case 2: Single object (convert to key-value table)
205 |     elif isinstance(data, dict):
206 |         lines = ['| Key | Value |']
207 |         lines.append('| --- | --- |')
208 |         for key, value in data.items():
209 |             # Convert value to string and escape pipes
210 |             if isinstance(value, bool):
211 |                 value_str = 'true' if value else 'false'
212 |             elif value is None:
213 |                 value_str = ''
214 |             elif isinstance(value, (list, dict)):
215 |                 value_str = json.dumps(value)
216 |             else:
217 |                 value_str = str(value)
218 |             value_str = value_str.replace('|', '\\|').replace('\n', ' ')
219 |             lines.append(f'| {key} | {value_str} |')
220 |         return '\n'.join(lines)
221 | 
222 |     # Case 3: Other types not supported
223 |     else:
224 |         return f"> [!CAUTION]\n> **Table Error:** JSON must be an array of objects or a single object for table conversion, got {type(data).__name__}"
```

### Usage Examples

**CSV Table:**
> [!CAUTION]
> **Table Error:** File not found: `data/users.csv`

**JSON Table:**
> [!CAUTION]
> **Table Error:** File not found: `data/users.json`

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

**Built-in Plugin Entry Points**

```toml
[project.entry-points."embedm.plugins"]
file = "embedm_plugins.file_plugin:FilePlugin"
layout = "embedm_plugins.layout_plugin:LayoutPlugin"
toc = "embedm_plugins.toc_plugin:TOCPlugin"
table = "embedm_plugins.table_plugin:TablePlugin"
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

<div style="display: flex; flex-direction: row; gap: 30px;">
<div style="flex: 0 0 50%;">

**Enable All Plugins (Default)**

```yaml
# Enable all discovered plugins (default)
plugins: "*"
```

</div>
<div style="flex: 0 0 50%;">

**Enable Specific Plugins**

```yaml
# Enable only specific plugins
plugins:
  - file
  - toc
  - table
```

</div>
</div>

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
