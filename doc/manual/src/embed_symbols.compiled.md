# Symbol Extraction Manual

This manual covers symbol-based code extraction in EmbedM, including dot notation, overload disambiguation, and namespace support.

## Table of Contents

  - [Overview](#overview)
  - [Basic Symbol Extraction](#basic-symbol-extraction)
    - [Extracting a Function](#extracting-a-function)
    - [Extracting a Class](#extracting-a-class)
    - [Extracting from JavaScript](#extracting-from-javascript)
    - [Extracting a SQL CTE](#extracting-a-sql-cte)
  - [Dot Notation](#dot-notation)
  - [Overload Disambiguation](#overload-disambiguation)
    - [How It Works](#how-it-works)
    - [Parameterless Overload](#parameterless-overload)
    - [Single Parameter Overload](#single-parameter-overload)
    - [Two Parameter Overload](#two-parameter-overload)
    - [Generic Types in Signatures](#generic-types-in-signatures)
  - [Namespace Support](#namespace-support)
    - [C# Namespace](#c-namespace)
    - [Full Qualified Path](#full-qualified-path)
  - [Combining with Other Properties](#combining-with-other-properties)
    - [Symbol with Line Numbers](#symbol-with-line-numbers)
    - [Symbol with Line Offset](#symbol-with-line-offset)
    - [Symbol with Title](#symbol-with-title)
  - [Symbol vs Lines vs Region](#symbol-vs-lines-vs-region)
  - [Complete Property Reference](#complete-property-reference)
- [Required](#required)
- [Optional - Content Selection](#optional---content-selection)
- [Optional - Line Numbers](#optional---line-numbers)
- [Optional - Presentation](#optional---presentation)
- [Optional - Documentation](#optional---documentation)
  - [Tips](#tips)

## Overview

The `symbol` property lets you embed a specific code symbol (function, class, method, etc.) by name instead of line numbers. This is more resilient to code changes since line numbers shift when code is edited, but symbol names typically stay the same.

Symbol extraction is supported for these languages:

| Language | Extensions | Supported Symbols |
|----------|-----------|-------------------|
| Python | `.py` | classes, functions, methods |
| JavaScript/TypeScript | `.js`, `.ts`, `.jsx`, `.tsx` | classes, functions, const/let/var |
| C# | `.cs` | namespaces, classes, interfaces, methods |
| Java | `.java` | packages, classes, interfaces, methods |
| C/C++ | `.c`, `.cpp`, `.h`, `.hpp` | namespaces, classes, structs, functions |
| SQL | `.sql` | CTEs, procedures, functions |

## Basic Symbol Extraction

### Extracting a Function

The simplest use is extracting a standalone function by name.

**Input:**
```yaml
type: file
source: examples/symbol_example.py
symbol: standalone_helper
```

**Output:**
```py
def standalone_helper(items):
    """A standalone utility function."""
    return [str(item) for item in items]
```

### Extracting a Class

Extract an entire class including all its methods.

**Input:**
```yaml
type: file
source: examples/symbol_example.py
symbol: Calculator
```

**Output:**
```py
class Calculator:
    """A basic calculator."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
```

### Extracting from JavaScript

Works the same way across languages.

**Input:**
```yaml
type: file
source: examples/symbol_example.js
symbol: EventEmitter
```

**Output:**
```js
class EventEmitter {
    constructor() {
        this.listeners = {};
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        const handlers = this.listeners[event] || [];
        handlers.forEach(fn => fn(data));
    }
}
```

### Extracting a SQL CTE

**Input:**
```yaml
type: file
source: examples/symbol_example.sql
symbol: monthly_totals
```

**Output:**
```sql
monthly_totals AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY user_id
)
```

## Dot Notation

Use dot notation to extract a specific method from a specific class. This is essential when multiple classes define methods with the same name.

**Input:**
```yaml
type: file
source: examples/symbol_example.py
symbol: Calculator.add
```

**Output:**
```py
def add(self, a, b):
    """Add two numbers."""
    return a + b
```

Dot notation first locates the `Calculator` class, then searches for `add` within it. If you had another class with an `add` method, this ensures you get the right one.

## Overload Disambiguation

When a class has multiple methods with the same name but different parameters (method overloading), use a signature suffix to select the right one.

### How It Works

Append `(param_types)` to the symbol name to filter by parameter types:

| Syntax | Meaning |
|--------|---------|
| `symbol: Render` | First method named `Render` (backward compatible) |
| `symbol: Render()` | The parameterless `Render` overload |
| `symbol: Render(string)` | The overload taking one `string` parameter |
| `symbol: Render(string, string)` | The overload taking two `string` parameters |

### Parameterless Overload

**Input:**
```yaml
type: file
source: examples/symbol_example.cs
symbol: Button.Render()
```

**Output:**
```cs
public void Render()
{
    Console.WriteLine("<button>Click me</button>");
}
```

### Single Parameter Overload

**Input:**
```yaml
type: file
source: examples/symbol_example.cs
symbol: Button.Render(string)
```

**Output:**
```cs
public void Render(string label)
{
    Console.WriteLine($"<button>{label}</button>");
}
```

### Two Parameter Overload

**Input:**
```yaml
type: file
source: examples/symbol_example.cs
symbol: Button.Render(string, string)
```

**Output:**
```cs
public void Render(string label, string style)
{
    Console.WriteLine($"<button style=\"{style}\">{label}</button>");
}
```

### Generic Types in Signatures

Angle brackets in generic types are handled correctly. Commas inside `<>` are not treated as parameter separators.

```yaml
type: file
source: mycode.cs
symbol: Process(Dictionary<string, int>, bool)
```

This matches a method with two parameters: `Dictionary<string, int>` and `bool`.

## Namespace Support

For languages with namespaces (C#, C++, Java), use dot notation to navigate the full path from namespace to symbol.

### C# Namespace

**Input:**
```yaml
type: file
source: examples/symbol_example.cs
symbol: Widgets.Button
```

**Output:**
```cs
class Button
{
    public void Render()
    {
        Console.WriteLine("<button>Click me</button>");
    }

    public void Render(string label)
    {
        Console.WriteLine($"<button>{label}</button>");
    }

    public void Render(string label, string style)
    {
        Console.WriteLine($"<button style=\"{style}\">{label}</button>");
    }
}
```

### Full Qualified Path

Combine namespace, class, and signature disambiguation for maximum precision.

**Input:**
```yaml
type: file
source: examples/symbol_example.cs
symbol: Widgets.Button.Render(string)
```

**Output:**
```cs
public void Render(string label)
{
    Console.WriteLine($"<button>{label}</button>");
}
```

## Combining with Other Properties

Symbol extraction works alongside other embed properties.

### Symbol with Line Numbers

**Input:**
```yaml
type: file
source: examples/symbol_example.py
symbol: Calculator
line_numbers: text
```

**Output:**
```py
 4 | class Calculator:
 5 |     """A basic calculator."""
 6 | 
 7 |     def add(self, a, b):
 8 |         """Add two numbers."""
 9 |         return a + b
10 | 
11 |     def multiply(self, a, b):
12 |         """Multiply two numbers."""
13 |         return a * b
```

### Symbol with Line Offset

After extracting a symbol, use `lines` to select a portion of it.

**Input:**
```yaml
type: file
source: examples/symbol_example.py
symbol: Calculator
lines: 1-3
```

**Output:**
```py
class Calculator:
    """A basic calculator."""
```

### Symbol with Title

**Input:**
```yaml
type: file
source: examples/symbol_example.py
symbol: standalone_helper
title: "Utility Function"
```

**Output:**
**Utility Function**

```py
def standalone_helper(items):
    """A standalone utility function."""
    return [str(item) for item in items]
```

## Symbol vs Lines vs Region

EmbedM offers three ways to select a portion of a file. Choose the right one for your use case:

| Property | Best For | Resilience to Code Changes |
|----------|----------|---------------------------|
| `lines: 10-20` | Quick one-off references | Low - breaks when lines shift |
| `region: name` | Sections you control | High - but requires adding markers to source |
| `symbol: name` | Functions, classes, methods | High - no markers needed, follows the code |

**Note:** `symbol` and `region` cannot be used together on the same embed. `lines` can be combined with `symbol` to select a portion of the extracted symbol.

## Complete Property Reference

```yaml
type: file

# Required
source: path/to/file.ext            # File path (relative to markdown file)

# Optional - Content Selection
lines: 10-20                         # Line range (e.g., 10-20, 15, 10-)
region: function_name                # Named region between md.start/end markers
symbol: ClassName.methodName         # Symbol name with optional dot notation
                                     # Append (types) for overloads: methodName(string)

# Optional - Line Numbers
line_numbers: text                   # Options: text, html, table, or omit
line_numbers_style: default          # For html: default, dark, minimal, or CSS file

# Optional - Presentation
title: "My Title"                    # Bold title above the embedded content

# Optional - Documentation
comment: "Explanation here"          # Not shown in output, for documentation only
```

## Tips

- **Start simple:** Use `symbol: name` first. Only add class or namespace prefixes when there is ambiguity.
- **No parens = first match:** `symbol: Render` returns the first method named `Render`. This is backward compatible and works well when there are no overloads.
- **Empty parens = parameterless:** `symbol: Render()` explicitly selects the overload with zero parameters.
- **Type names are flexible:** `string` will match `System.String`, and matching is case-insensitive.
- **Comments are ignored:** Symbol extraction skips over commented-out code, so a symbol name inside a comment won't cause a false match.
