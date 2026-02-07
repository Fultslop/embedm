# EmbedM
version 0.4

A Python tool for embedding files, code snippets, and generating tables of contents in Markdown documents with built-in safety limits and validation.

EmbedM is part of a bigger initiative to explore how far we can push the current state of the art LLMs. This project has been built mainly using [Claude Sonnet 4.5](https://claude.ai/) and [Google Gemini 3](https://gemini.google.com/app).

## What is EmbedM?

EmbedM processes Markdown files by resolving special embed blocks that reference external files or generate content dynamically. It features a three-phase pipeline architecture that validates all operations before execution, ensuring safe and predictable processing.

## Features

### Core Features
- **File Embedding**: Embed entire files or specific portions into Markdown documents
- **Line Range Selection**: Extract specific line ranges using `L10-20` syntax
- **Named Regions**: Extract code sections marked with `md.start:name` and `md.end:name` tags
- **Line Numbers**: Display embedded code with text or HTML-formatted line numbers
- **CSV to Table**: Automatically convert CSV files to Markdown tables
- **Table of Contents**: Generate GitHub-style table of contents from document headings
- **Layout Embeds**: Create multi-column/row layouts with flexbox-based positioning and styling
- **Recursive Embedding**: Embed Markdown files that contain their own embeds
- **YAML-Based Syntax**: Clean, extensible YAML format with syntax highlighting
- **Batch Processing**: Process individual files or entire directories

### Safety & Validation
- **Three-Phase Pipeline**: Discovery → Validation → Execution
- **Comprehensive Validation**: Check all files, limits, and dependencies before processing
- **Safety Limits**: Configurable limits on file sizes, recursion depth, embed counts, and more
- **Circular Dependency Detection**: Automatically detect and report infinite loops
- **Fail Fast**: All errors reported upfront with file:line references
- **Force Mode**: Optional `--force` flag to embed warnings in output and continue processing
- **Helpful Error Messages**: Clear guidance on how to fix issues or override limits

## Project Structure

EmbedM is organized as a modular Python package with clear separation of concerns:

```
embedm/
├── pyproject.toml          # Modern Python project configuration
├── src/embedm/
│   ├── __init__.py        # Public API exports
│   ├── __main__.py        # Module execution support
│   ├── cli.py            # Command-line interface with argparse
│   ├── models.py         # Data structures (Limits, ValidationResult, etc.)
│   ├── discovery.py      # File and embed discovery
│   ├── validation.py     # Validation phase logic
│   ├── parsing.py        # YAML embed block parsing
│   ├── extraction.py     # Region and line extraction
│   ├── formatting.py     # Line number formatting
│   ├── converters.py     # CSV and TOC generation
│   ├── layout.py         # Layout embed processing (flexbox)
│   ├── processors.py     # File embed processing
│   └── resolver.py       # Core resolution logic with limit checking
└── tests/                 # Comprehensive test suite
```

The codebase follows a clean architecture with focused modules, making it easy to maintain, test, and extend.

## Installation

### From Source (Recommended for Development)

```bash
git clone https://github.com/Fultslop/embedm.git
cd embedm
pip install -e .
```

This installs embedm in editable mode with all dependencies (PyYAML) and creates the `embedm` command.

### Traditional Method

```bash
git clone https://github.com/Fultslop/embedm.git
cd embedm
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- PyYAML>=6.0

### Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs additional development tools including pytest.

## Usage

### Basic Usage

After installing with `pip install -e .`, you can use the `embedm` command directly:

```bash
# Process a single file (creates input.compiled.md)
embedm input.md

# Process with custom output
embedm input.md output.md

# Process a directory
embedm source_dir/ output_dir/

# Validate without processing (dry run)
embedm input.md --dry-run

# View all available options
embedm --help
```

### Alternative: Module Execution

You can also run embedm as a Python module:
```bash
python -m embedm input.md
```

### Safety Limits

EmbedM includes configurable safety limits to prevent resource exhaustion and catch common errors:

```bash
# Override individual limits
embedm input.md --max-file-size 5MB
embedm input.md --max-recursion 10
embedm input.md --max-embeds 200

# Override multiple limits
embedm input.md \
  --max-file-size 5MB \
  --max-recursion 10 \
  --max-embeds 200 \
  --max-output-size 20MB \
  --max-embed-text 5KB

# Disable specific limits (use 0)
embedm input.md --max-recursion 0  # Unlimited recursion
```

**Default Limits:**
- `--max-file-size`: 1MB (input file size)
- `--max-recursion`: 8 (maximum recursion depth)
- `--max-embeds`: 100 (embeds per file)
- `--max-output-size`: 10MB (output file size)
- `--max-embed-text`: 2KB (embedded content length)

**Size Formats:** `1024`, `1KB`, `1K`, `1MB`, `1M`, `1GB`, `1G`

### Force Mode

Use `--force` to continue processing even when validation errors occur. Errors will be embedded in the output as warnings:

```bash
embedm input.md --force
```

When using `--force`, missing files or exceeded limits will appear in the compiled output:

```markdown
> [!CAUTION]
> **Embed Error:** File not found: `missing_file.txt`
```

```markdown
> [!CAUTION]
> **File Size Limit Exceeded:** Source file `large.txt` size 5.0MB exceeds
> limit 1.0MB. Use `--max-file-size` to increase this limit.
```

This is useful for:
- Previewing partial results while debugging
- Working with incomplete documentation
- Seeing exactly where limits are being exceeded

### Validation Pipeline

EmbedM uses a three-phase pipeline architecture that validates all operations before execution:

#### Phase 1: Discovery & Validation
```
🔍 Validation Phase
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Discovered: 5 files, 23 embeds
  Dependencies: max depth 4
  ✅ All validations passed
```

During this phase, EmbedM:
- Discovers all files to process
- Parses all embed directives (without executing them)
- Builds a dependency graph
- Validates all limits and checks:
  - All source files exist
  - No circular dependencies
  - File sizes within limits
  - Recursion depth acceptable
  - Embed counts within limits
  - All regions/line ranges are valid

#### Phase 2: Reporting

All errors and warnings are displayed together with file:line references:

```
❌ Errors Found (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  doc/api.md:15
    └─ Source file not found: examples/missing.py

  doc/embed_loops.md
    └─ Circular dependency detected: loop.md -> embed_loops.md
```

The tool exits before any processing if errors are found (unless `--force` is used).

#### Phase 3: Execution

Only runs if validation passes (or `--force` is enabled):

```
⚙️  Processing Phase
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ api.md → compiled/api.md
  ✅ guide.md → compiled/guide.md
  ✅ reference.md → compiled/reference.md

✅ Processing complete (3 files, 2.3s)
```

This architecture ensures:
- **Fail Fast**: All errors reported upfront, not one-by-one
- **No Partial Writes**: Files only written if all validation passes
- **Better Debugging**: See all issues at once
- **Safety**: Limits checked before any file operations

## Embed Syntax

EmbedM uses YAML code blocks with `type: embed.*` to define embeds. This provides syntax highlighting and a clean, extensible format.

### Embed Entire File

````markdown
```yaml
type: embed.file
source: path/to/file.py
```
````

### Embed with Line Numbers

````markdown
```yaml
type: embed.file
source: path/to/file.py
line_numbers: html
```
````

**Line number options:**
- `text` - Plain text line numbers (e.g., `1 | code here`)
- `html` - Styled HTML with non-selectable line numbers
- `false` - No line numbers (default)

### Embed Specific Lines

````markdown
```yaml
type: embed.file
source: path/to/file.py
region: L10-20
```
````

**Region formats supported:**
- `L10` - Single line
- `L10-20` - Line range
- `L10-L20` - Line range (alternative syntax)
- `L10-` - From line 10 to end of file

### Embed Named Region

````markdown
```yaml
type: embed.file
source: path/to/file.py
region: myfunction
```
````

Mark regions in your source files:
```python
# md.start:myfunction
def my_function():
    pass
# md.end:myfunction
```

### Embed with Title

````markdown
```yaml
type: embed.file
source: path/to/file.py
title: Example Implementation
```
````

### Combine Multiple Options

````markdown
```yaml
type: embed.file
source: path/to/file.py
region: L10-50
line_numbers: html
title: Core Implementation
```
````

### Generate Table of Contents

Generate a table of contents from the current document's headings:

````markdown
```yaml
type: embed.toc
```
````

Alternative (both work):
````markdown
```yaml
type: embed.table_of_contents
```
````

Generate a table of contents from a specific file:

````markdown
```yaml
type: embed.toc
source: path/to/document.md
```
````

**TOC Properties:**
- `source`: Optional path to file to generate TOC from. If not specified, generates from current document's headings.

**Note:** When using TOC in layouts, the `source` property is **required** to specify which file's headings to include.

### Embed CSV as Table

````markdown
```yaml
type: embed.file
source: data.csv
```
````

CSV files are automatically converted to Markdown tables.

### Layout Embeds

Create multi-column or multi-row layouts using flexbox-based positioning.

**Basic Two-Column Layout:**

````markdown
```yaml
type: embed.layout
orientation: row
gap: 20px
sections:
  - size: 50%
    embed:
      type: embed.file
      source: left-content.md
  - size: 50%
    embed:
      type: embed.file
      source: right-content.md
```
````

**Layout with Styling:**

````markdown
```yaml
type: embed.layout
orientation: row
gap: 15px
border: "1px solid #ccc"
padding: 20px
background: "#f9f9f9"
sections:
  - size: 30%
    border: "2px solid #007bff"
    padding: 15px
    background: "#e7f3ff"
    embed:
      type: embed.toc
      source: main-content.md
  - size: 70%
    padding: 15px
    embed:
      type: embed.file
      source: main-content.md
```
````

**Scrollable Sidebar Layout:**

````markdown
```yaml
type: embed.layout
orientation: row
gap: 20px
sections:
  - size: 250px
    max-height: 600px
    overflow-y: auto
    overflow-x: hidden
    padding: 15px
    border: "1px solid #ddd"
    background: "#f8f9fa"
    embed:
      type: embed.toc
      source: content.md
  - size: auto
    embed:
      type: embed.file
      source: content.md
```
````

This creates a fixed-width sidebar (250px) with scrollable overflow when the table of contents exceeds 600px height, while the main content area takes up remaining space.

**Layout Properties:**

Container-level properties:
- `orientation`: `row` (horizontal) or `column` (vertical) - default: `row`
- `gap`: Space between sections (e.g., `20px`, `10%`) - default: `0`
- `border`: Container border (e.g., `"1px solid #ccc"`, `true`) - optional
- `padding`: Container padding (e.g., `20px`, `5%`) - optional
- `background`: Container background color or CSS background - optional
- `overflow`: Overflow behavior (`auto`, `scroll`, `hidden`, `visible`) - optional
- `overflow-x`: Horizontal overflow (overrides `overflow` for x-axis) - optional
- `overflow-y`: Vertical overflow (overrides `overflow` for y-axis) - optional
- `max-height`: Maximum height (e.g., `500px`, `80vh`) - optional
- `max-width`: Maximum width (e.g., `1200px`, `90%`) - optional
- `min-height`: Minimum height (e.g., `300px`) - optional
- `min-width`: Minimum width (e.g., `200px`) - optional

Section properties (per section in `sections` list):
- `size`: Section size (`auto`, `50%`, `300px`) - default: `auto`
- `border`: Section border - optional
- `padding`: Section padding - optional
- `background`: Section background - optional
- `overflow`: Section overflow behavior - optional
- `overflow-x`: Section horizontal overflow - optional
- `overflow-y`: Section vertical overflow - optional
- `max-height`: Section maximum height - optional
- `max-width`: Section maximum width - optional
- `min-height`: Section minimum height - optional
- `min-width`: Section minimum width - optional
- `embed`: Nested embed directive (file, toc, or another layout) - required

**Size Specifications:**

- `auto` - Section grows/shrinks to fit content (uses `flex: 1 1 auto`)
- `50%` - Fixed percentage of container
- `300px` - Fixed pixel size
- If no size specified, defaults to `auto`

**Important Notes:**

- **Color Values**: In YAML, colors starting with `#` must be quoted (e.g., `"#ccc"`) because `#` is a comment character
- **Border Shorthand**: `border: true` uses default `1px solid #ccc`
- **Nested Layouts**: Layouts can contain other layouts for complex grid structures
- **Rendering**: Uses inline CSS flexbox, compatible with most markdown renderers
- **Overflow Defaults**: Overflow defaults to `visible` (no scrollbars). Use `overflow: auto` to add scrollbars when content exceeds size
- **Scrollable Sections**: Combine `max-height` or `max-width` with `overflow: auto` for scrollable regions
- **Viewport Units**: You can use viewport units like `80vh` (80% of viewport height) for responsive max-height values

**Use Cases:**

- Side-by-side code comparisons
- Documentation with scrollable sidebar navigation
- Dashboard-style layouts with multiple panels
- Multi-column feature lists
- Fixed-height content previews with scroll
- Responsive layouts with viewport-based dimensions

## Examples

### Example 1: Documentation with Code Examples

````markdown
# API Documentation

## Authentication

```yaml
type: embed.file
source: examples/auth.py
region: L15-30
line_numbers: text
title: Authentication Example
```

## Error Handling

```yaml
type: embed.file
source: examples/errors.py
region: error_handler
```
````

### Example 2: Project README with TOC

````markdown
# My Project

```yaml
type: embed.toc
```

## Installation
...

## Usage
...
````

### Example 3: Recursive Embedding

Create reusable sections:

**sections/features.md:**
````markdown
## Key Features

- Fast processing
- Easy to use
````

**README.md:**
````markdown
# Product

```yaml
type: embed.file
source: sections/features.md
```
````

### Example 4: Documentation with Sidebar Layout

Create a documentation page with table of contents sidebar:

````markdown
# User Guide

```yaml
type: embed.layout
orientation: row
gap: 20px
padding: 20px
border: "1px solid #e0e0e0"
sections:
  - size: 25%
    background: "#f5f5f5"
    padding: 15px
    border: "1px solid #ddd"
    embed:
      type: embed.toc
      source: guide-content.md
  - size: 75%
    padding: 15px
    embed:
      type: embed.file
      source: guide-content.md
```

## Getting Started
...
````

For more examples see the [examples directory](https://github.com/Fultslop/embedm/tree/main/doc/examples/src)

## Common Use Cases & Troubleshooting

### Working with Large Files

If you encounter file size limit errors:

```bash
# Increase file size limit
embedm large-doc.md --max-file-size 10MB

# Or disable the limit entirely
embedm large-doc.md --max-file-size 0
```

### Deep Nesting / Recursion

For deeply nested embed structures:

```bash
# Increase recursion limit
embedm nested-docs.md --max-recursion 15

# Or disable recursion limit
embedm nested-docs.md --max-recursion 0
```

### Many Embeds in One File

If a file has many embed directives:

```bash
# Increase embed count limit
embedm complex-doc.md --max-embeds 500
```

### Debugging Validation Errors

Use `--dry-run` to validate without processing:

```bash
# Check for errors without writing files
embedm source_dir/ output_dir/ --dry-run
```

Use `--force` to see partial results:

```bash
# Process with errors, warnings embedded in output
embedm incomplete-doc.md --force
```

### Circular Dependencies

If you get circular dependency errors:

```
❌ Circular dependency detected: a.md -> b.md -> a.md
```

Review your embed chain to identify the loop. Each file should only embed files that don't reference it back.

## Testing

Run the test suite:
```bash
python tests/test_embedm.py
```

Run with verbose output:
```bash
python tests/test_embedm.py -v
```

Or use pytest (recommended):
```bash
pytest tests/ -v
```

## Project Configuration

EmbedM uses `pyproject.toml` for modern Python project configuration, following PEP 518 standards. This provides:

- **Single Configuration File**: All project metadata, dependencies, and tool settings in one place
- **Standard Packaging**: Easy to install, distribute, and publish to PyPI
- **CLI Entry Point**: Automatic `embedm` command registration
- **Development Tools**: Integrated pytest and coverage configuration
- **Dependency Management**: Clear separation between runtime and development dependencies

The `pyproject.toml` file makes it easy to:
- Install for development: `pip install -e .`
- Install with dev tools: `pip install -e ".[dev]"`
- Build distributions: `python -m build`
- Publish to PyPI: `twine upload dist/*`

## Why YAML Format?

The YAML-based syntax provides several advantages:

1. **Syntax Highlighting**: YAML blocks get proper syntax highlighting in editors and on GitHub
2. **Clean Structure**: Properties are clearly defined with key-value pairs
3. **Extensibility**: Easy to add new embed types (e.g., `embed.layout`) without breaking existing syntax
4. **Type Safety**: The `type` field clearly identifies what kind of embed it is
5. **Familiar**: YAML is widely used and understood by developers

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.
