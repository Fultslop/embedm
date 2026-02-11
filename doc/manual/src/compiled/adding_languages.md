# Adding Language Support

This tutorial walks through adding a new language to EmbedM's symbol extraction system, using Go as a worked example.

## Table of Contents

  - [Overview](#overview)
  - [The Data Model](#the-data-model)
    - [SymbolPattern](#symbolpattern)
    - [CommentStyle](#commentstyle)
    - [LanguageConfig](#languageconfig)
  - [Step 1: Identify the Language's Syntax](#step-1-identify-the-languages-syntax)
  - [Step 2: Define the CommentStyle](#step-2-define-the-commentstyle)
  - [Step 3: Write the Symbol Patterns](#step-3-write-the-symbol-patterns)
    - [Struct Pattern](#struct-pattern)
    - [Interface Pattern](#interface-pattern)
    - [Function Pattern](#function-pattern)
    - [Method Pattern](#method-pattern)
    - [Pattern Order](#pattern-order)
  - [Step 4: Assemble the Config](#step-4-assemble-the-config)
  - [Step 5: Register the Config](#step-5-register-the-config)
  - [Step 6: Test It](#step-6-test-it)
    - [Extract a Struct](#extract-a-struct)
    - [Extract an Interface](#extract-an-interface)
    - [Extract a Function](#extract-a-function)
    - [Extract a Method](#extract-a-method)
  - [Checklist](#checklist)

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

```py
@dataclass
class SymbolPattern:
    """A pattern for matching a type of symbol in a language.

    Attributes:
        kind: Human-readable label (e.g., 'function', 'class', 'cte')
        regex_template: Regex with {name} placeholder for the symbol name.
        block_style: One of 'brace', 'paren', 'indent', 'keyword'
        keyword_end: For 'keyword' style - closing keyword regex (e.g., r'\\bEND\\b')
        nestable: Whether this symbol can contain nested symbols (for dot notation)
    """
    kind: str
    regex_template: str
    block_style: str
    keyword_end: Optional[str] = None
    nestable: bool = True
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

```py
@dataclass
class CommentStyle:
    """Defines how a language handles comments and strings.

    Attributes:
        line_comment: Line comment prefix (e.g., '#', '//')
        block_comment_start: Block comment opening (e.g., '/*')
        block_comment_end: Block comment closing (e.g., '*/')
        string_delimiters: String delimiter characters
        triple_quote: Whether triple-quoted strings are supported (Python)
    """
    line_comment: Optional[str] = None
    block_comment_start: Optional[str] = None
    block_comment_end: Optional[str] = None
    string_delimiters: List[str] = field(default_factory=lambda: ['"', "'"])
    triple_quote: bool = False
```

### LanguageConfig

Brings everything together: a name, the file extensions it handles, and the ordered list of patterns to try.

```py
@dataclass
class LanguageConfig:
    """Complete language definition for symbol extraction.

    Attributes:
        name: Language name (for error messages)
        extensions: File extensions this config handles (without dot)
        comment_style: How comments and strings work
        patterns: Ordered list of SymbolPatterns to try
    """
    name: str
    extensions: List[str]
    comment_style: CommentStyle
    patterns: List[SymbolPattern]
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

**examples/symbol_example.go**

```go
 1 | package server
 2 | 
 3 | import "fmt"
 4 | 
 5 | // Config holds server configuration.
 6 | type Config struct {
 7 | 	Host    string
 8 | 	Port    int
 9 | 	Verbose bool
10 | }
11 | 
12 | // Handler defines the request handling interface.
13 | type Handler interface {
14 | 	ServeHTTP(path string) string
15 | 	Middleware(next Handler) Handler
16 | }
17 | 
18 | // NewConfig creates a Config with sensible defaults.
19 | func NewConfig(host string, port int) Config {
20 | 	return Config{
21 | 		Host:    host,
22 | 		Port:    port,
23 | 		Verbose: false,
24 | 	}
25 | }
26 | 
27 | // Address returns the host:port string.
28 | func (c Config) Address() string {
29 | 	return fmt.Sprintf("%s:%d", c.Host, c.Port)
30 | }
31 | 
32 | // SetVerbose enables verbose logging.
33 | func (c *Config) SetVerbose(enabled bool) {
34 | 	c.Verbose = enabled
35 | }
36 |
```

### Extract a Struct

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: Config
```

**Output:**
```go
type Config struct {
	Host    string
	Port    int
	Verbose bool
}
```

### Extract an Interface

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: Handler
```

**Output:**
```go
type Handler interface {
	ServeHTTP(path string) string
	Middleware(next Handler) Handler
}
```

### Extract a Function

**Input:**
```yaml
type: file
source: examples/symbol_example.go
symbol: NewConfig
```

**Output:**
```go
func NewConfig(host string, port int) Config {
	return Config{
		Host:    host,
		Port:    port,
		Verbose: false,
	}
}
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
```go
func (c Config) Address() string {
	return fmt.Sprintf("%s:%d", c.Host, c.Port)
}
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
