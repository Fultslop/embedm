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
- [quote_plugin.py](#quote-pluginpy)
    - [Usage](#usage)
    - [Output](#output)
  - [Example 2: Metadata Plugin](#example-2-metadata-plugin)
- [metadata_plugin.py](#metadata-pluginpy)
    - [Usage](#usage-1)
    - [Output](#output-1)
  - [Registering Your Plugin](#registering-your-plugin)
    - [Step 1: Package Your Plugin](#step-1-package-your-plugin)
    - [Step 2: Define Entry Point](#step-2-define-entry-point)
    - [Step 3: Install Your Plugin](#step-3-install-your-plugin)
- [Install in development mode](#install-in-development-mode)
- [Or install from package](#or-install-from-package)
    - [Step 4: Verify Discovery](#step-4-verify-discovery)
  - [Configuring Plugins](#configuring-plugins)
    - [Enable All Plugins (Default)](#enable-all-plugins-default)
    - [Enable Specific Plugins](#enable-specific-plugins)
    - [Configuration Precedence](#configuration-precedence)
  - [Development Tips](#development-tips)
    - [1. Error Handling](#1-error-handling)
- [Good](#good)
- [Bad - don't do this](#bad---dont-do-this)
    - [2. Use Utility Methods](#2-use-utility-methods)
- [Path resolution](#path-resolution)
- [File existence check](#file-existence-check)
- [Consistent error formatting](#consistent-error-formatting)
    - [3. Handle Context and Limits](#3-handle-context-and-limits)
    - [4. Cycle Detection](#4-cycle-detection)
- [Add to stack before processing](#add-to-stack-before-processing)
- [Pass new_stack to nested embeds](#pass-new-stack-to-nested-embeds)
    - [5. Multi-Phase Plugins](#5-multi-phase-plugins)
    - [6. Testing Your Plugin](#6-testing-your-plugin)
    - [7. Documentation](#7-documentation)
  - [Summary](#summary)

## Overview

Plugins in EmbedM handle specific embed types like `file`, `layout`, or `toc`. The plugin system is based on:

1. **Plugin Interface**: All plugins implement the `EmbedPlugin` abstract base class
2. **Entry Points**: Plugins are discovered automatically via Python entry points
3. **Registry**: A central registry routes embed processing to the correct plugin
4. **Configuration**: Users can enable/disable plugins via `embedm_config.yaml`

### Built-in Plugins

EmbedM includes three built-in plugins:

- **FilePlugin**: Embeds files and code snippets (`file`)
- **LayoutPlugin**: Creates multi-column/row layouts (`layout`)
- **TOCPlugin**: Generates table of contents (`toc`)

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

```py

@property
@abstractmethod
def name(self) -> str:
    """Unique plugin identifier (e.g., 'file', 'toc', 'csv')."""
    pass

@property
@abstractmethod
def embed_types(self) -> List[str]:
    """List of embed type strings this plugin handles.

    Example: ['file'] handles 'type: file' in yaml embedm blocks
    """
    pass

@property
@abstractmethod
def phases(self) -> List['ProcessingPhase']:
    """Processing phases when this plugin executes.

    A plugin can run in multiple phases if needed (e.g., comment removal
    runs in both EMBED and POST_PROCESS for cleanup).

    Returns:
        List of ProcessingPhase values (e.g., [ProcessingPhase.EMBED])
        or [ProcessingPhase.EMBED, ProcessingPhase.POST_PROCESS] for multi-phase
    """
    pass

@property
@abstractmethod
def valid_properties(self) -> List[str]:
    """List of valid property names for this plugin.

    The 'type' and 'comment' properties are always valid and handled
    separately - don't include them in this list.

    Example:
        return ["source", "title", "lines", "region", "line_numbers"]

    Returns:
        List of valid property names (strings)
    """
    pass
```

### Required Method

```py

@abstractmethod
def process(
    self,
    properties: Dict,
    current_file_dir: str,
    processing_stack: Set[str],
    context: Optional['ProcessingContext'] = None
) -> str:
    """Process the embed and return content.

    Args:
        properties: Parsed YAML properties (source, title, etc.)
        current_file_dir: Absolute directory of the Markdown file containing the embed
        processing_stack: Set of files currently being processed (for cycle detection)
        context: Processing context with limits and state tracking

    Returns:
        Processed content as string (Markdown or HTML)
        Error message in format: "> [!CAUTION]\n> **Error:** Message"
    """
    pass
```

### Utility Methods

The base class provides helpful utilities:

```py

def resolve_path(self, source: str, current_file_dir: str) -> str:
    """Resolve relative path to absolute path.

    Args:
        source: Source path (may be relative)
        current_file_dir: Base directory for relative paths

    Returns:
        Absolute path
    """
    return os.path.abspath(os.path.join(current_file_dir, source))

def format_error(self, category: str, message: str) -> str:
    """Format error message in standard style.

    Args:
        category: Error category (e.g., "File Not Found", "Limit Exceeded")
        message: Error message

    Returns:
        Formatted error block
    """
    return f"> [!CAUTION]\n> **{category}:** {message}"

def check_file_exists(self, file_path: str) -> Optional[str]:
    """Check if file exists, return error if not.

    Args:
        file_path: Path to check

    Returns:
        None if file exists, error string if not
    """
    if not os.path.exists(file_path):
        return self.format_error("File Not Found", f"`{file_path}`")
    if os.path.isdir(file_path):
        return self.format_error("Invalid File", f"`{file_path}` is a directory")
    return None

def check_limit(
    self,
    value: int,
    limit: int,
    category: str,
    value_desc: str,
    limit_desc: str
) -> Optional[str]:
    """Check if value exceeds limit, return error if so.

    Args:
        value: Current value to check
        limit: Maximum allowed value
        category: Error category
        value_desc: Description of current value (formatted)
        limit_desc: Description of limit (formatted)

    Returns:
        None if within limit, error string if exceeded
    """
    if limit > 0 and value > limit:
        return self.format_error(
            f"{category} Limit Exceeded",
            f"{value_desc} exceeds limit {limit_desc}"
        )
    return None
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
        quote_lines = [f"> *{text}*"]

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
type: quote
text: "The only way to do great work is to love what you do."
author: Steve Jobs
```

### Output

> *The only way to do great work is to love what you do.*
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

```toml
[project.entry-points."embedm.plugins"]
file = "embedm_plugins.file_plugin:FilePlugin"
layout = "embedm_plugins.layout_plugin:LayoutPlugin"
toc = "embedm_plugins.toc_plugin:TOCPlugin"
table = "embedm_plugins.table_plugin:TablePlugin"
comment = "embedm_plugins.comment_plugin:CommentPlugin"
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
        type: mytype
        source: str (required) - Path to source file
        format: str (optional) - Output format (default: 'auto')
        title: str (optional) - Title for output

    Example:
        ```yaml
        type: mytype
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
