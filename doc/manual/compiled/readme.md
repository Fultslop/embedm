# EmbedM

> [!NOTE]
> This project is to test the capabilities of AI code assistants. The first iteration yielded valuable insights but ultimately failed to produce valuable code. If you want to see the result, see the archive folder. The next iteration (2) has just started.
> The readme still reflects the intentions of the project, so it's allowed to stay around.


Iteration 2 

version 0.6.0

Safely embed files, code, and content directly into Markdown — and keep them in sync.

  - [Why EmbedM?](#why-embedm)
  - [See It In Action](#see-it-in-action)
  - [Quick Start](#quick-start)
  - [Features](#features)
  - [Documentation](#documentation)
  - [Safety and Validation](#safety-and-validation)
  - [Project Background](#project-background)
  - [License](#license)
  - [Contributing](#contributing)

## Why EmbedM?

If you've ever copied code into documentation, later changed the code, and forgot to update the docs — your documentation is already out of date.

EmbedM lets you embed code, data, and file fragments directly from source files into Markdown, safely and repeatably. When the source changes, recompile and your docs are up-to-date.

## See It In Action

You add an embed directive to your Markdown (inside a ` ```yaml embedm ` fenced block):

````yaml
type: file
source: examples/demo.py
region: connect
````

EmbedM produces:

```py
def connect(host, port=5432, timeout=30):
    """Establish a database connection."""
    conn = Database.connect(
        host=host,
        port=port,
        timeout=timeout,
    )
    return conn
```

The embedded code is pulled directly from the source file. When `demo.py` changes, the docs update automatically on the next compile.

You can also extract by symbol name — no region markers needed:

````yaml
type: file
source: examples/demo.py
symbol: query
````

```py
def query(conn, sql, params=None):
    """Execute a parameterized query safely."""
    cursor = conn.cursor()
    cursor.execute(sql, params or [])
    return cursor.fetchall()
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

- **File access sandbox** — restricts source paths to the project root by default
- **Safety limits** — configurable caps on file size, recursion depth, embed count, and output size

- **Line numbers** — text or styled HTML line numbers
- **CSV/Json to table** — automatic Markdown table conversion
- **Table of contents** — generated from document headings
- **Layouts** — multi-column/row flexbox-based layouts
- **Recursive embedding** — Markdown files that embed other Markdown files
- **Simplified mermaid charts** - Add mermaid flowcharts using a shorthand notation.

## Documentation

## Safety and Validation

EmbedM uses a three-phase pipeline — **Discovery, Validation, Execution** — that checks all files, limits, and dependencies before writing any output. Errors are reported upfront with file:line references. A file access sandbox restricts embeds to the project root (detected via git), with `--allow-path` for exceptions.

Use `--dry-run` to validate without processing, or `--force` to embed warnings in the output and continue.

## Project Background

EmbedM is part of an exploration into how far AI-assisted development can go when building a non-trivial, production-style tool. This project has been built primarily using [Claude](https://claude.ai/) and [Google Gemini](https://gemini.google.com/app).

The goal is not just to demo AI, but to see whether AI-assisted development can produce software that is readable, testable, maintainable, and genuinely useful.

The first iteration of this project was a usable proof of concept. Concepts were explored, the projects scope was set and features were delivered (unless halicunated). However, the code driving these features was "less than optimial". Having unittests, test coverage and regression tests was not enough to keep the AI on track. The result of this first iteration can be found in [the archive](./archive/iteration_1/).

Based on these findings, reading up on people with similar experiences and consulting with a knowledgable AI assistant or two, the next iteration would add some more guardrails:

* Create an document outlining the goals and constraint of the project and code.
* Identifying core features and create a scaffolding to which the ai has to stick.
* Add more automation tooling to detect the AI going off rails. 

## License

MIT License — see LICENSE file for details.

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.
