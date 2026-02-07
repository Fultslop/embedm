# EmbedM 
version 0.2

A Python tool for embedding files, code snippets, and generating tables of contents in Markdown documents.

EmbedM is part of a bigger initiative to explore how far we can push the current state of the art LLMs. This project has been built mainly using [Claude Sonnet 4.5](https://claude.ai/) and [Google Gemini 3](https://gemini.google.com/app).

## What is EmbedM?

EmbedM processes Markdown files by resolving special embed blocks that reference external files or generate content dynamically. It enables you to maintain a single source of truth for code examples, documentation snippets, and structured data while keeping your Markdown files clean and maintainable.

## Features

- **File Embedding**: Embed entire files or specific portions into Markdown documents
- **Line Range Selection**: Extract specific line ranges using `L10-20` syntax
- **Named Regions**: Extract code sections marked with `md.start:name` and `md.end:name` tags
- **Line Numbers**: Display embedded code with text or HTML-formatted line numbers
- **CSV to Table**: Automatically convert CSV files to Markdown tables
- **Table of Contents**: Generate GitHub-style table of contents from document headings
- **Recursive Embedding**: Embed Markdown files that contain their own embeds
- **YAML-Based Syntax**: Clean, extensible YAML format with syntax highlighting
- **Batch Processing**: Process individual files or entire directories

## Installation

```bash
git clone https://github.com/Fultslop/embedm.git
cd embedm
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- PyYAML

## Usage

### Basic Usage

Process a single file:
```bash
python src/embedm.py input.md
```

Process a single file with custom output:
```bash
python src/embedm.py input.md output.md
```

Process a directory:
```bash
python src/embedm.py source_dir/ output_dir/
```

## Embed Syntax

EmbedM uses YAML code blocks with `type: embed.*` to define embeds. This provides syntax highlighting and a clean, extensible format.

### Embed Entire File

```markdown
```yaml
type: embed.file
source: path/to/file.py
```
```

### Embed with Line Numbers

```markdown
```yaml
type: embed.file
source: path/to/file.py
line_numbers: html
```
```

**Line number options:**
- `text` - Plain text line numbers (e.g., `1 | code here`)
- `html` - Styled HTML with non-selectable line numbers
- `false` - No line numbers (default)

### Embed Specific Lines

```markdown
```yaml
type: embed.file
source: path/to/file.py
region: L10-20
```
```

**Region formats supported:**
- `L10` - Single line
- `L10-20` - Line range
- `L10-L20` - Line range (alternative syntax)
- `L10-` - From line 10 to end of file

### Embed Named Region

```markdown
```yaml
type: embed.file
source: path/to/file.py
region: myfunction
```
```

Mark regions in your source files:
```python
# md.start:myfunction
def my_function():
    pass
# md.end:myfunction
```

### Embed with Title

```markdown
```yaml
type: embed.file
source: path/to/file.py
title: Example Implementation
```
```

### Combine Multiple Options

```markdown
```yaml
type: embed.file
source: path/to/file.py
region: L10-50
line_numbers: html
title: Core Implementation
```
```

### Generate Table of Contents

```markdown
```yaml
type: embed.toc
```
```

Alternative (both work):
```markdown
```yaml
type: embed.table_of_contents
```
```

### Embed CSV as Table

```markdown
```yaml
type: embed.file
source: data.csv
```
```

CSV files are automatically converted to Markdown tables.

## Examples

### Example 1: Documentation with Code Examples

```markdown
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
```

### Example 2: Project README with TOC

```markdown
# My Project

```yaml
type: embed.toc
```

## Installation
...

## Usage
...
```

### Example 3: Recursive Embedding

Create reusable sections:

**sections/features.md:**
```markdown
## Key Features

- Fast processing
- Easy to use
```

**README.md:**
```markdown
# Product

```yaml
type: embed.file
source: sections/features.md
```
```

## Testing

Run the test suite:
```bash
python tests/test_embedm.py
```

Run with verbose output:
```bash
python tests/test_embedm.py -v
```

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
