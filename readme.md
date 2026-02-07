# EmbedM 
version 0.1

A Python tool for embedding files, code snippets, and generating tables of contents in Markdown documents.

EmbedM is part of a bigger initiative to explore how far we can push the current state of the art LLMs. This project has been build mainly using [Claude Sonnet 4.5](https://claude.ai/) and [Google Gemini 3](https://gemini.google.com/app).

## What is EmbedM?

EmbedM processes Markdown files by resolving special `embed` blocks that reference external files or generate content dynamically. It enables you to maintain a single source of truth for code examples, documentation snippets, and structured data while keeping your Markdown files clean and maintainable.

## Features

- **File Embedding**: Embed entire files or specific portions into Markdown documents
- **Line Range Selection**: Extract specific line ranges using `L10-20` syntax
- **Named Regions**: Extract code sections marked with `md.start:name` and `md.end:name` tags
- **Line Numbers**: Display embedded code with text or HTML-formatted line numbers
- **CSV to Table**: Automatically convert CSV files to Markdown tables
- **Table of Contents**: Generate GitHub-style table of contents from document headings
- **Recursive Embedding**: Embed Markdown files that contain their own embeds
- **Safety Limits**: Configurable limits for file size, recursion depth, and embed count
- **Batch Processing**: Process individual files or entire directories

## Installation

```bash
git clone https://github.com/Fultslop/embedm.git
cd embedm
```

No additional dependencies required - uses Python standard library only.

## Usage

### Basic Usage

Process a single file:
```bash
python embedm.py input.md
```

Process a single file with custom output:
```bash
python embedm.py input.md output.md
```

Process a directory:
```bash
python embedm.py source_dir/ output_dir/
```


## Embed Syntax

### Embed Entire File

```markdown
```embed
file: path/to/file.py
```
```

### Embed with Line Numbers

```markdown
```embed
file: path/to/file.py
line_numbers: html
```
```

Options: `text` (plain text), `html` (styled HTML), `false` (none)

### Embed Specific Lines

```markdown
```embed
file: path/to/file.py#L10-20
```
```

Formats supported:
- `L10` - Single line
- `L10-20` - Line range
- `L10-L20` - Line range (alternative syntax)
- `L10-` - From line 10 to end of file

### Embed Named Region

```markdown
```embed
file: path/to/file.py#myfunction
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
```embed
file: path/to/file.py
title: Example Implementation
```
```

### Generate Table of Contents

```markdown
```embed
table_of_contents
```
```

### Embed CSV as Table

```markdown
```embed
file: data.csv
```
```

## Testing

Run the test suite:
```bash
python test_embedm.py
```

Run with verbose output:
```bash
python test_embedm.py -v
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.