# File Embedding Manual

This manual covers file embedding in EmbedM, including all line numbering options and their limitations.

## Table of Contents

  - [Overview](#overview)
  - [Basic File Embedding](#basic-file-embedding)
  - [Embedding Specific Sections](#embedding-specific-sections)
    - [Line Ranges](#line-ranges)
    - [Named Regions](#named-regions)
  - [Line Numbers](#line-numbers)
    - [No Line Numbers (Default)](#no-line-numbers-default)
    - [Text Line Numbers](#text-line-numbers)
    - [HTML Line Numbers (Styled)](#html-line-numbers-styled)
    - [Table Line Numbers (GitHub-Compatible)](#table-line-numbers-github-compatible)
  - [Comparison: Which Line Number Format to Use?](#comparison-which-line-number-format-to-use)
    - [Recommendations](#recommendations)
  - [Adding Titles](#adding-titles)
  - [Recursive Markdown Embedding](#recursive-markdown-embedding)
- [Nested Documentation Example](#nested-documentation-example)
  - [Code Example](#code-example)
  - [Another Section](#another-section)
  - [Size Limits and Safety](#size-limits-and-safety)
  - [Complete Property Reference](#complete-property-reference)
  - [Examples in This Manual](#examples-in-this-manual)
  - [Advanced: Custom HTML Line Number Themes](#advanced-custom-html-line-number-themes)

## Overview

The `file` embed type allows you to embed external files or portions of files into your markdown documents. This is useful for:

- Including code examples from actual source files
- Embedding configuration files
- Showing specific functions or code sections
- Maintaining DRY documentation that stays in sync with code

## Basic File Embedding

The simplest file embed requires only a `source` property.

**Input:**
```yaml
type: file
source: examples/basic_example.py
```

**Output:**
```py
"""Basic Python example for file embedding."""


def hello():
    """Print a greeting."""
    print("Hello, world!")


def add(a, b):
    """Add two numbers."""
    return a + b


if __name__ == "__main__":
    hello()
    print(add(2, 3))
```

This embeds the entire file wrapped in a markdown code block with automatic language detection based on the file extension.

## Embedding Specific Sections

### Line Ranges

Use the `lines` property to embed specific line ranges.

**Input:**
```yaml
type: file
source: examples/sections_example.py
lines: 10-20
```

**Output:**
```py
    """Second function (lines 9-14)."""
    for i in range(3):
        print(f"Iteration {i}")
    return "done"


def function_three():
    """Third function (lines 17-22)."""
    data = {
        "key1": "value1",
        "key2": "value2"
```

You can also use:
- Single lines: `lines: 15`
- From line to end: `lines: 10-`

### Named Regions

For more semantic section selection, use named regions with `md.start:name` and `md.end:name` markers.

**Input:**
```yaml
type: file
source: examples/regions_example.py
region: main_function
```

**Output:**
```py
def main_function(name):
    """
    The main function that we want to embed.

    This section is marked with md.start:main_function
    and md.end:main_function markers.
    """
    result = helper_function()
    print(f"Hello, {name}! Result: {result}")
    return result
```

The markers themselves are not included in the output, and indentation is automatically adjusted.

## Line Numbers

EmbedM supports four different line numbering formats, each with different use cases and limitations.

### No Line Numbers (Default)

When `line_numbers` is omitted, the file is embedded as a standard markdown code block.

**Input:**
```yaml
type: file
source: examples/basic_example.py
lines: 4-6
```

**Output:**
```py
def hello():
    """Print a greeting."""
    print("Hello, world!")
```

**Use When:**
- Code should be easily copy-pasteable
- No line references are needed
- Viewing in any markdown renderer

**Limitations:**
- None - this is the most compatible format

### Text Line Numbers

Add `line_numbers: text` for simple text-based line numbers.

**Input:**
```yaml
type: file
source: examples/basic_example.py
lines: 4-6
line_numbers: text
```

**Output:**
```py
4 | def hello():
5 |     """Print a greeting."""
6 |     print("Hello, world!")
```

**Use When:**
- Need line numbers for reference
- Want maximum compatibility
- Viewing on GitHub or any markdown renderer
- Want copyable code (though includes line numbers)

**Limitations:**
- Line numbers are part of the code block (copy-paste includes them)
- No visual styling options
- Takes up horizontal space

### HTML Line Numbers (Styled)

Add `line_numbers: html` for styled, non-selectable line numbers with theme support.

**Input:**
```yaml
type: file
source: examples/basic_example.py
lines: 4-6
line_numbers: html
line_numbers_style: default
```

**Output:**
<div style="background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; line-height: 1.5;">
<pre style="margin: 0; overflow: visible;"><code class="language-py"><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">4</span>def hello():
</span><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">5</span>    &quot;&quot;&quot;Print a greeting.&quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">6</span>    print(&quot;Hello, world!&quot;)
</span></code></pre>
</div>

**Available Themes:**
- `default` - GitHub's light theme colors
- `dark` - Dark theme for dark-mode documentation
- `minimal` - Simple border-only styling
- Custom CSS file path (relative or absolute)

**Use When:**
- Building documentation sites (MkDocs, Docusaurus, etc.)
- Viewing in VS Code preview
- Want professional-looking line numbers
- Need non-selectable line numbers

**Limitations:**
- ❌ **Does NOT work on GitHub** - GitHub strips inline styles and `<style>` blocks for security
- Only works in environments that allow custom HTML/CSS
- More complex output

**GitHub Compatibility:**
On GitHub, HTML line numbers will render as plain unstyled HTML. The code will be visible but without any styling. Use `text` or `table` formats for GitHub instead.

### Table Line Numbers (GitHub-Compatible)

Add `line_numbers: table` for GitHub-compatible line numbers in a markdown table.

**Input:**
```yaml
type: file
source: examples/basic_example.py
lines: 4-6
line_numbers: table
```

**Output:**
| Line | Code |
|-----:|------|
| 4 | `def hello():` |
| 5 | `    """Print a greeting."""` |
| 6 | `    print("Hello, world!")` |

**Use When:**
- Publishing to GitHub
- Need visual separation between line numbers and code
- Want line numbers that work everywhere
- Don't need code to be easily copyable

**Limitations:**
- Code is in table cells with backticks (not continuous)
- Copy-paste includes table structure
- Each line is individually formatted (may affect syntax highlighting in some viewers)
- Takes up more vertical space than other formats

## Comparison: Which Line Number Format to Use?

| Format | GitHub | Copy-Paste | Styled | Best For |
|--------|--------|------------|--------|----------|
| None | ✅ | ✅ Perfect | N/A | General use, copyable code |
| Text | ✅ | ⚠️ Includes line numbers | ❌ | Line references, maximum compatibility |
| HTML | ❌ Broken | ✅ Code only | ✅ | Documentation sites, VS Code preview |
| Table | ✅ | ❌ Table structure | ⚠️ Basic | GitHub, visual separation |

### Recommendations

1. **For GitHub README files:** Use `text` or `table`
2. **For documentation sites (MkDocs, etc.):** Use `html` with your preferred theme
3. **For copyable code examples:** Omit `line_numbers`
4. **For VS Code-only documentation:** Use `html`

## Adding Titles

Add a `title` property to include a bold title above the embedded content.

**Input:**
```yaml
type: file
source: examples/basic_example.py
lines: 4-6
title: "Example: Basic Function"
```

**Output:**
**Example: Basic Function**

```py
def hello():
    """Print a greeting."""
    print("Hello, world!")
```

## Recursive Markdown Embedding

When embedding markdown files (`.md`), EmbedM recursively processes any embeds within them.

**Input:**
```yaml
type: file
source: examples/nested_doc.md
title: "Nested Documentation Example"
```

**Output:**
**Nested Documentation Example**

# Nested Documentation Example

This markdown file contains embeds that will be resolved when this file is embedded elsewhere.

## Code Example

Here's a Python function:

```py
def hello():
    """Print a greeting."""
    print("Hello, world!")
```

## Another Section

This demonstrates recursive embedding - when this file is embedded using `type: file`, all the embeds within it will also be processed.

**Function Two from sections_example.py**

```py
def function_two():
    """Second function (lines 9-14)."""
    for i in range(3):
        print(f"Iteration {i}")
    return "done"
```

This creates truly modular documentation!


This allows you to build modular documentation where markdown files can include other files and have their embeds resolved.

## Size Limits and Safety

EmbedM has built-in safety limits to prevent processing extremely large files:

- **Max file size:** Default 1MB (configurable with `--max-file-size`)
- **Max embed text:** Default 100KB (configurable with `--max-embed-text`)
- **Max recursion depth:** Default 10 (configurable with `--max-recursion-depth`)

If a file exceeds these limits, you'll see a clear error message with instructions on how to increase the limit.

## Complete Property Reference

```yaml
type: file

# Required
source: path/to/file.ext        # File path (relative to markdown file)

# Optional - Content Selection
lines: 10-20                    # Line range (e.g., 10-20, 15, 10-)
region: function_name            # Named region between md.start/end markers

# Optional - Line Numbers
line_numbers: text               # Options: text, html, table, or omit
line_numbers_style: default      # For html: default, dark, minimal, or CSS file path

# Optional - Presentation
title: "My Title"                # Bold title above the embedded content

# Optional - Documentation
comment: "Explanation here"      # Not shown in output, for documentation only
```

## Examples in This Manual

This manual itself uses EmbedM! The table of contents at the top was generated with `type: toc`, and all the examples above use `type: file` embeds to show real code from the `examples/` directory.

## Advanced: Custom HTML Line Number Themes

When using `line_numbers: html`, you can create custom CSS themes. Create a `.css` file with these classes:

```css
.code-block-mytheme {
  /* Container styles */
}
.code-block-mytheme pre {
  /* Code block styles */
}
.code-block-mytheme .line-number {
  /* Line number styles - must include user-select: none */
}
```

Then reference it:

```yaml
type: file
source: mycode.py
line_numbers: html
line_numbers_style: path/to/mytheme.css
```

**Note:** Custom CSS themes also don't work on GitHub due to the same style sanitization.
