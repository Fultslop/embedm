# EmbedM

version 0.9.10

A Markdown compiler driven by source files.

  - [Project Background](#project-background)
  - [How It Works](#how-it-works)
  - [Use Cases](#use-cases)
    - [Keeping code documentation in sync](#keeping-code-documentation-in-sync)
    - [Live metadata in a README or changelog](#live-metadata-in-a-readme-or-changelog)
    - [Data tables without copy-paste](#data-tables-without-copy-paste)
    - [CI drift detection](#ci-drift-detection)
    - [AI agent context documents](#ai-agent-context-documents)
  - [Directives](#directives)
  - [Quick Start](#quick-start)
  - [Features](#features)
  - [Documentation](#documentation)
  - [License](#license)
  - [Contributing](#contributing)

## Project Background

EmbedM is part of an exploration into how far AI-assisted development can go when building a non-trivial tool that could be used in a production CD/CI chain. This project has been built based on a _human_ defined architecture, functional spec and a series of interface contracts, then implemented using using [Claude](https://claude.ai/) and to a lesser extent [Google Gemini](https://gemini.google.com/app). 

## How It Works

EmbedM compiles Markdown documents from directive blocks. Each directive references a source — a code file, a data query, a CSV table, or another document — and is replaced with the extracted, formatted content on compile. Change the source; recompile; the document is current.

## Use Cases

### Keeping code documentation in sync

Embed a function directly from the source file, scoped by a named region or by symbol name. When the implementation changes the docs regenerate on the next compile — no copy-paste, no drift. Instead of copying the function code, you simply add a reference to the class/function/method/enum or struct.

Instead of adding code that may go out of date:

```java
public void createUser(string user) {
    // ...
}
```

You create a link to said method, which will be replaced with the up-to-date function at compile time, or give a clear error in case the method 'createUser' is no longer there.

````yaml
type: file
source: src/api/handlers.java
symbol: UserHandler.createUser
title: "POST /users"
link: true
````

### Live metadata in a README or changelog

Pull version numbers, project names, and other values from `pyproject.toml`, `package.json`, or any JSON/YAML/TOML/XML file. The version at the top of this page is a live example — it is compiled from `pyproject.toml` at build time. Instead of a hard coded version, create a reference to the project. Eg:

````yaml
type: query-path
source: pyproject.toml
path: project.version
format: "Released: **v{value}**"
````

### Data tables without copy-paste

Embed CSV, TSV data or structured json as formatted Markdown tables. Apply column selection, filtering, and sorting inline — the source file is the single source of truth via:

````yaml
type: table
source: reports/q4-summary.csv
select: "Region as Region, Revenue as Revenue_USD"
order_by: "Revenue_USD desc"
limit: 10
````

### CI drift detection

Use `--verify` in your pipeline to catch documentation that has fallen behind its sources. Exit code 1 if any compiled file is stale.

```
embedm ./docs/src --verify -d ./docs/compiled
```

### AI agent context documents

Use `recall` to query a large document — a devlog, a decision log, an ADR set — and extract the sentences most relevant to a given topic. Compose multiple queries into a single compiled context file that an AI assistant reads at session start.

````yaml
type: recall
source: ./devlog.md
query: "validation transform boundary error handling"
max_sentences: 5
````

EmbedM itself uses this: its agent context file is compiled from the project devlog using four targeted recall queries — plugin conventions, architectural rules, common mistakes, and the active spec. The context window stays focused without manual curation.

## Directives

Directives are fenced YAML blocks tagged `` ```yaml embedm ``. On compile, each is replaced in-place with the extracted content:

````yaml
type: file
source: src/config/defaults.py
region: connection_defaults
````

```python
# connection_defaults
HOST = "localhost"
PORT = 5432
TIMEOUT = 30
POOL_SIZE = 10
```

Structured data queries render inline:

````yaml
type: query-path
source: config/app.yaml
path: database.pool_size
format: "Default pool size: **{value}**"
````

> Default pool size: **10**

## Quick Start

**Install**

```
pip install embedm
```

Or from source:

```
git clone https://github.com/Fultslop/embedm.git
cd embedm
pip install -e .
```

**Compile a single file**

```
embedm content.md -o compiled/content.md
```

**Compile a directory**

```
embedm ./docs/src -d ./docs/compiled
```

**Preview without writing**

```
embedm content.md -n
```

**Check that compiled files are up to date**

```
embedm ./docs/src --verify -d ./docs/compiled
```

**Generate a default config file**

```
embedm --init
```

**Creating new plugins**

See the [plugin_tutorial](./doc/manual/src/assets/tutorial/plugin_tutorial.md)

## Features

**File embedding**
- Embed entire files, line ranges (`5..10`), or named regions (`md.start:name` / `md.end:name`)
- Markdown sources are merged inline; all other types are wrapped in a fenced code block
- Optional title, source link, and line-number annotation

**Symbol extraction**
- Extract classes and methods by name from C/C++, C#, and Java source files
- Dot-notation for nested symbols: `OuterClass.InnerClass.methodName`
- Overload disambiguation: `add(int, int)` vs `add(int, int, int)`

**Structured data**
- Query any value from JSON, YAML, TOML, or XML using dot-notation paths
- Scalars render inline; dicts and lists render as YAML code blocks
- Format strings for inline interpolation: `"version {value}"`

**Data tables**
- Render CSV and TSV files as Markdown tables
- Column selection, row filtering (exact match and comparison operators), sorting, pagination

**Table of contents**
- Auto-generated from document headings, including headings in embedded files
- GitHub-compatible anchor links

**AI context**
- `synopsis` — generate a condensed summary of a document
- `recall` — build structured retrieval blocks for AI agent context files

**Recursive embedding**
- Markdown files that embed other Markdown files, up to a configurable depth

**Safety**
- Configurable limits on file size, memory, recursion depth, and embed output size
- `--verify` mode for CI drift detection

## Documentation

| Document | Description |
|----------|-------------|
| [CLI Reference](doc/manual/compiled/cli.md) | All flags, input modes, and exit codes |
| [Configuration Reference](doc/manual/compiled/configuration.md) | `embedm-config.yaml` properties and defaults |
| [File Plugin](doc/manual/compiled/file_plugin.md) | File embedding, regions, lines, symbol extraction |
| [Query-Path Plugin](doc/manual/compiled/query_path_plugin.md) | Structured data extraction from JSON/YAML/TOML/XML |
| [Table Plugin](doc/manual/compiled/table_plugin.md) | CSV/TSV tables with filtering and sorting |
| [Toc Plugin](doc/manual/compiled/toc_plugin.md) | Table-of-contents generation |
| [Architecture](doc/manual/compiled/architecture.md) | System design, plugin model, plan/compile pipeline |

## License

MIT License — see LICENSE file for details.

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.
