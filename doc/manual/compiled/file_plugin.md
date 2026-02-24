# File Plugin

version 0.9.0

The file plugin embeds the contents of an external file into your document. Markdown files are merged inline; all other file types are wrapped in a fenced code block, with the file extension used as the language hint. Optional extraction by region, line range, or language symbol narrows the output to exactly the part you need.

  - [Basic Usage](#basic-usage)
  - [Extraction Options](#extraction-options)
    - [Region](#region)
    - [Lines](#lines)
    - [Symbol](#symbol)
  - [Display Options](#display-options)
    - [title](#title)
    - [link](#link)
    - [line_numbers_range](#line-numbers-range)
  - [Combining Options](#combining-options)
  - [Recursive Compilation](#recursive-compilation)
  - [Symbol Reference](#symbol-reference)
    - [Supported Languages](#supported-languages)
    - [How Resolution Works](#how-resolution-works)
    - [Overload Disambiguation](#overload-disambiguation)
    - [Adding a New Language](#adding-a-new-language)
  - [Plugin Configuration](#plugin-configuration)

## Basic Usage

Embed a file with `type: file` and a `source` path. Paths are resolved relative to the directory of the file containing the directive.

Non-markdown sources are wrapped in a fenced code block:

```yaml
type: file
source: ./example_symbols.java
```

```java
public class Calculator {

    // md.start:simple-add
    public int add(int a, int b) {
        return a + b;
    }
    // md.end:simple-add

    public int add(int a, int b, int c) {
        return a + b + c;
    }

    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("division by zero");
        }
        return numerator / denominator;
    }
}
```
Markdown sources are embedded inline — their content is merged directly into the output:

```yaml
type: file
source: ./example_snippet.md
```

This is an **example snippet** embedded from `example_snippet.md`.

- Markdown content is merged inline into the output document.
- Any valid markdown is preserved: headings, lists, code, and links.

## Extraction Options

Three options let you embed a portion of the source: `region`, `lines`, and `symbol`. They are mutually exclusive — only one may be specified per directive.

### Region

Mark sections of a file with `md.start:<name>` and `md.end:<name>` comments, then reference them by name. The marker lines are excluded from the output.

```yaml
type: file
source: ./example_symbols.java
region: simple-add
```

```java
    public int add(int a, int b) {
        return a + b;
    }
```
### Lines

Extract a contiguous range with `lines`. Line numbers are 1-based.

Supported formats: `"10"` (single line), `"5..10"` (inclusive range), `"5.."` (from line to end), `"..10"` (from start to line).

```yaml
type: file
source: ./example_symbols.java
lines: "9..11"
```

```java
    public int add(int a, int b, int c) {
        return a + b + c;
    }
```
### Symbol

Extract a named declaration by identifier. Supported for C/C++, C#, and Java source files. The extractor walks the declaration tree, so inner symbols can be reached with dot notation.

```yaml
type: file
source: ./example_symbols.java
symbol: Calculator.divide
```

```java
    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("division by zero");
        }
        return numerator / denominator;
    }
```
When a method is overloaded, append a parameter signature to select the exact variant:

```yaml
type: file
source: ./example_symbols.java
symbol: Calculator.add(int, int, int)
```

```java
    public int add(int a, int b, int c) {
        return a + b + c;
    }
```
## Display Options

Display options add a header line above the embedded block. They can be combined with each other and with any extraction option.

### title

`title` prepends a bold label:

```yaml
type: file
source: ./example_symbols.java
symbol: Calculator.divide
title: "Divide"
```

> **"Divide"**
```java
    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("division by zero");
        }
        return numerator / denominator;
    }
```
### link

`link: true` appends a relative link to the source file:

```yaml
type: file
source: ./example_symbols.java
region: simple-add
link: true
```

> [link example_symbols.java](../src/example_symbols.java)
```java
    public int add(int a, int b) {
        return a + b;
    }
```
### line_numbers_range

`line_numbers_range: true` appends the extracted line range to the header. This option only adds output when used together with `lines`.

```yaml
type: file
source: ./example_symbols.java
lines: "13..18"
line_numbers_range: true
```

> (lines 13..18)
```java
    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("division by zero");
        }
        return numerator / denominator;
    }
```
## Combining Options

All display options compose freely. This example labels an extracted range, links to the source, and shows the line numbers:

```yaml
type: file
source: ./example_symbols.java
lines: "13..18"
title: "divide"
link: true
line_numbers_range: true
```

> **"divide"** (lines 13..18) [link example_symbols.java](../src/example_symbols.java)
```java
    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new ArithmeticException("division by zero");
        }
        return numerator / denominator;
    }
```
## Recursive Compilation

When the source is a markdown file containing embedm directives, the file plugin compiles it recursively before embedding the result. Each nested directive is resolved by the same plugin registry, up to the configured `max_recursion` depth (default 8).

The `plugin_sequence` setting in `embedm-config.yaml` controls the order in which plugins run during recursive compilation. When an embedded file contains multiple directive types, `plugin_sequence` determines which transformations happen first — for example, ensuring a `query-path` data lookup is resolved before a `synopsis` reads the same content. Plugins not listed in the sequence run last, in discovery order.

## Symbol Reference

### Supported Languages

Symbol extraction is available for files with the following extensions:

| Language | Extensions |
|----------|------------|
| C/C++    | `.c`, `.cpp`, `.h`, `.hpp`, `.cc`, `.cxx` |
| C#       | `.cs` |
| Java     | `.java` |

Each language supports a set of symbol kinds. C/C++ recognises namespaces, classes, structs, enums, and functions. C# adds interfaces and file-scoped namespaces. Java covers classes, interfaces, enums, and methods.

### How Resolution Works

For a symbol like `MyClass.myMethod`, the extractor:

1. Splits on dots to form a scope chain: `["MyClass", "myMethod"]`.
2. Scans the file for the first nestable symbol named `MyClass` (class, namespace, etc.).
3. Descends into that block and scans for `myMethod`.
4. Returns the complete source block, including its opening and closing braces.

The scanner runs a string and comment state machine, so identifiers inside string literals or comments are not matched. Chains can be as deep as needed: `OuterNs.InnerClass.TargetMethod` works for any nesting depth.

### Overload Disambiguation

Append a parameter signature to resolve a specific overload:

```
symbol: Calculator.add(int, int)      # selects the two-argument add
symbol: Calculator.add(int, int, int) # selects the three-argument add
symbol: Calculator.noArgs()           # selects the zero-argument overload
```

Parameter types are matched case-insensitively and support suffix matching, so `String` matches `java.lang.String`. Modifiers such as `final`, `ref`, `out`, and default values are stripped before comparison.

When no signature is given and the name is ambiguous, the first matching declaration is returned.

### Adding a New Language

Language support is defined by a `LanguageConfig` in `src/embedm/parsing/symbol_parser.py`. Each entry specifies:

- `name`: display name used in error messages.
- `extensions`: list of file extensions (without the leading dot).
- `comment_style`: a `CommentStyle` with `line_comment`, `block_comment_start`, `block_comment_end`, and `string_delimiters`.
- `patterns`: an ordered list of `SymbolPattern` objects. Each pattern has:
  - `kind`: a human-readable label (e.g. `"class"`, `"method"`).
  - `regex_template`: a regex with a `{name}` placeholder that matches the declaration line.
  - `block_style`: `"brace"` for `{}`-delimited blocks, or `"rest_of_file"` for file-scoped constructs (e.g. C# file-scoped namespaces).
  - `nestable`: `True` if this symbol kind can contain other nestable symbols (used for dot-notation scoping).

Once defined, add the config to `_EXTENSION_MAP` at the bottom of the file. The map is keyed by extension string, so a config covering multiple extensions must be included once per extension.

## Plugin Configuration

Region marker templates can be customised per project in `embedm-config.yaml`. Both templates must contain `{tag}`, which is replaced at extraction time with the region name.

```yaml
plugin_configuration:
  embedm_plugins.file_plugin:
    region_start: "// region:{tag}"
    region_end: "// endregion:{tag}"
```

The defaults are `md.start:{tag}` and `md.end:{tag}`.
