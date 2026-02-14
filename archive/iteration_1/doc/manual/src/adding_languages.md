# Adding Language Support

This tutorial walks through adding a new language to EmbedM's symbol extraction system, using Go as a worked example.

## Table of Contents

```yaml embedm
type: toc
```

## Overview

Symbol extraction is driven by declarative language configs in `src/embedm/symbols.py`. Adding a new language requires no changes to the extraction engine itself — you only need to define:

1. **CommentStyle** — how to skip comments and strings
2. **SymbolPatterns** — regex patterns for each symbol type
3. **LanguageConfig** — ties it all together with a name and file extensions

The extraction engine uses these configs to find symbols, skip commented-out code, and determine block boundaries automatically.

## The Data Model

Before writing a config, it helps to understand the three dataclasses that make up the system.

### SymbolPattern

Each pattern describes one kind of symbol the language supports.

```yaml embedm
type: file
source: ../../../src/embedm/symbols.py
symbol: SymbolPattern
```

The key fields:

- **`kind`** — a label like `"function"`, `"class"`, or `"struct"`. Used in error messages.
- **`regex_template`** — a regex with a `{name}` placeholder. The engine substitutes the requested symbol name at runtime. Must match the declaration line.
- **`block_style`** — tells the engine how to find the end of the symbol's body. Options:

| Block Style | How It Finds the End | Languages |
|-------------|---------------------|-----------|
| `brace` | Counts `{` and `}` to find matching close | C#, Java, Go, C++, JS |
| `indent` | Follows indentation level | Python |
| `paren` | Counts `(` and `)` to find matching close | SQL CTEs |
| `keyword` | Scans for a closing keyword (e.g., `END`) | SQL procedures |
| `rest_of_file` | Everything from the match to EOF | Java packages, file-scoped C# namespaces |

- **`nestable`** — set to `True` for symbols that can contain other symbols (classes, namespaces, structs). This enables dot notation like `ClassName.methodName`.

### CommentStyle

Tells the engine how to recognize and skip comments and strings so that a symbol name inside a comment is never matched.

```yaml embedm
type: file
source: ../../../src/embedm/symbols.py
symbol: CommentStyle
```

### LanguageConfig

Brings everything together: a name, the file extensions it handles, and the ordered list of patterns to try.

```yaml embedm
type: file
source: ../../../src/embedm/symbols.py
symbol: LanguageConfig
```

## Step 1: Identify the Language's Syntax

Before writing any code, catalog the language's relevant features:

| Feature | Go |
|---------|-----|
| Line comments | `//` |
| Block comments | `/* ... */` |
| String delimiters | `"` and `` ` `` (backtick for raw strings) |
| Structs | `type Name struct { ... }` |
| Interfaces | `type Name interface { ... }` |
| Functions | `func Name(...) { ... }` |
| Methods | `func (r Type) Name(...) { ... }` |
| Block delimiters | `{` and `}` for all symbols |

All Go symbols use brace-delimited blocks, which keeps the config simple.

## Step 2: Define the CommentStyle

Go uses C-style comments and has two string delimiter types:

```py
comment_style=CommentStyle(
    line_comment="//",
    block_comment_start="/*",
    block_comment_end="*/",
    string_delimiters=['"', '`'],
),
```

The `triple_quote` field defaults to `False`, which is correct for Go (only Python needs it set to `True`).

## Step 3: Write the Symbol Patterns

Work through each symbol type, writing a regex that matches its declaration line.

### Struct Pattern

Go structs are declared as `type Name struct {`:

```py
SymbolPattern(
    kind="struct",
    regex_template=r'^\s*type\s+{name}\s+struct\b',
    block_style="brace",
    nestable=True,
),
```

- `^\s*` — allows leading whitespace
- `type\s+{name}\s+struct\b` — matches the exact Go syntax
- `nestable=True` — structs can contain nested type definitions in dot notation

### Interface Pattern

Go interfaces follow the same `type Name interface {` pattern:

```py
SymbolPattern(
    kind="interface",
    regex_template=r'^\s*type\s+{name}\s+interface\b',
    block_style="brace",
    nestable=True,
),
```

### Function Pattern

Go functions are declared with `func Name(`:

```py
SymbolPattern(
    kind="function",
    regex_template=r'^\s*func\s+{name}\s*[\(\[]',
    block_style="brace",
),
```

The `[\(\[]` matches either `(` (parameters) or `[` (type parameters in generics).

### Method Pattern

Go methods have a receiver before the name: `func (r Type) Name(`:

```py
SymbolPattern(
    kind="method",
    regex_template=r'^\s*func\s+\([^)]+\)\s+{name}\s*\(',
    block_style="brace",
),
```

- `\([^)]+\)` — matches the receiver `(c Config)` or `(c *Config)`
- The method pattern is separate from the function pattern because the receiver changes the regex structure

### Pattern Order

Patterns are tried in order. Place more specific patterns first if there could be ambiguity. For Go, the order doesn't matter much since struct/interface/function/method declarations are syntactically distinct.

## Step 4: Assemble the Config

Combine everything into a `LanguageConfig`:

```py
GO_CONFIG = LanguageConfig(
    name="Go",
    extensions=["go"],
    comment_style=CommentStyle(
        line_comment="//",
        block_comment_start="/*",
        block_comment_end="*/",
        string_delimiters=['"', '`'],
    ),
    patterns=[
        SymbolPattern(
            kind="struct",
            regex_template=r'^\s*type\s+{name}\s+struct\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="interface",
            regex_template=r'^\s*type\s+{name}\s+interface\b',
            block_style="brace",
            nestable=True,
        ),
        SymbolPattern(
            kind="function",
            regex_template=r'^\s*func\s+{name}\s*[\(\[]',
            block_style="brace",
        ),
        SymbolPattern(
            kind="method",
            regex_template=r'^\s*func\s+\([^)]+\)\s+{name}\s*\(',
            block_style="brace",
        ),
    ],
)
```

## Step 5: Register the Config

Add the new config to the `ALL_CONFIGS` list at the bottom of the language configs section in `symbols.py`:

```py
ALL_CONFIGS = [PYTHON_CONFIG, JS_TS_CONFIG, ..., GO_CONFIG]
```

This is all that's needed — the engine builds an extension-to-config lookup automatically. No other files need to change.

## Step 6: Test It

With the config registered, symbol extraction works immediately. Here is the Go example file we will use for testing:

```yaml embedm
type: file
source: examples/symbol_example.go
line_numbers: text
title: "examples/symbol_example.go"
```

### Extract a Struct

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: Config
```

**Output:**
```yaml embedm
type: file
source: examples/symbol_example.go
symbol: Config
```

### Extract an Interface

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: Handler
```

**Output:**
```yaml embedm
type: file
source: examples/symbol_example.go
symbol: Handler
```

### Extract a Function

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: NewConfig
```

**Output:**
```yaml embedm
type: file
source: examples/symbol_example.go
symbol: NewConfig
```

### Extract a Method

Methods with receivers work the same way — just use the method name:

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: Address
```

**Output:**
```yaml embedm
type: file
source: examples/symbol_example.go
symbol: Address
```

## Checklist

When adding a new language, verify each of these:

- [ ] All symbol types extract correctly (struct, function, class, etc.)
- [ ] Comments containing symbol names are skipped
- [ ] Strings containing symbol names are skipped
- [ ] Nested symbols work with dot notation if `nestable=True`
- [ ] Multi-line declarations are handled (brace on next line, etc.)
- [ ] The `kind` labels are descriptive (they appear in error messages)
- [ ] File extensions don't conflict with existing configs
- [ ] Add tests in `tests/test_symbols.py` for the new language
