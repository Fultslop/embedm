# EmbedM
version 0.4.0

Embed files, code, and content directly into Markdown — and keep them in sync.

```yaml embedm
type: toc
```

## Why EmbedM?

If you've ever copied code into documentation, later changed the code, and forgot to update the docs — your documentation is already out of date.

EmbedM lets you embed code, data, and file fragments directly from source files into Markdown, safely and repeatably. When the source changes, recompile and your docs are current.

## See It In Action

You add an embed directive to your Markdown (inside a ` ```yaml embedm ` fenced block):

````yaml
type: file
source: examples/demo.py
region: connect
````

EmbedM produces:

```yaml embedm
type: file
source: examples/demo.py
region: connect
```

The embedded code is pulled directly from the source file. When `demo.py` changes, the docs update automatically on the next compile.

You can also extract by symbol name — no region markers needed:

````yaml
type: file
source: examples/demo.py
symbol: query
````

```yaml embedm
type: file
source: examples/demo.py
symbol: query
```

## Quick Start

```
git clone https://github.com/Fultslop/embedm.git
cd embedm
pip install -e .
```

Then:

```
embedm input.md                    # creates input.compiled.md
embedm input.md output.md          # explicit output
embedm docs/src/ docs/compiled/    # batch process a directory
embedm input.md --dry-run          # validate without writing
```

## Features

- **File embedding** — entire files or specific line ranges (`L10-20`)
- **Named regions** — extract sections marked with `md.start:name` / `md.end:name`
- **Symbol extraction** — embed functions, classes, or methods by name (Python, JS, C#, Java, C/C++, Go, SQL)
- **Line numbers** — text or styled HTML line numbers
- **CSV to table** — automatic Markdown table conversion
- **Table of contents** — generated from document headings
- **Layouts** — multi-column/row flexbox-based layouts
- **Recursive embedding** — Markdown files that embed other Markdown files
- **Safety limits** — configurable caps on file size, recursion depth, embed count, and output size
- **File access sandbox** — restricts source paths to the project root by default

## Documentation

| Manual | Description |
|--------|-------------|
| [File Embedding](doc/manual/src/compiled/embed_file.md) | Embedding files, line ranges, regions, and line numbers |
| [Symbol Extraction](doc/manual/src/compiled/embed_symbols.md) | Extracting functions, classes, and methods by name |
| [CLI Reference](doc/manual/src/compiled/cli.md) | All command-line options, limits, and sandbox configuration |
| [Plugin System](doc/manual/src/compiled/plugins.md) | Writing custom embed plugins |
| [Adding Languages](doc/manual/src/compiled/adding_languages.md) | Adding symbol extraction for new programming languages |

## Safety and Validation

EmbedM uses a three-phase pipeline — **Discovery, Validation, Execution** — that checks all files, limits, and dependencies before writing any output. Errors are reported upfront with file:line references. A file access sandbox restricts embeds to the project root (detected via git), with `--allow-path` for exceptions.

Use `--dry-run` to validate without processing, or `--force` to embed warnings in the output and continue.

## Project Background

EmbedM is part of an exploration into how far AI-assisted development can go when building a non-trivial, production-style tool. This project has been built primarily using [Claude](https://claude.ai/) and [Google Gemini](https://gemini.google.com/app).

The goal is not just to demo AI, but to see whether AI-assisted development can produce software that is readable, testable, maintainable, and genuinely useful.

## License

MIT License — see LICENSE file for details.

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.
