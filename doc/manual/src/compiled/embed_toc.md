# Table of Contents Manual

This manual covers table of contents generation in EmbedM — automatically creating navigable TOCs from markdown headings.

## Table of Contents

  - [Overview](#overview)
  - [Basic Usage (Current Document)](#basic-usage-current-document)
    - [Where to Place the TOC](#where-to-place-the-toc)
  - [TOC from External Files](#toc-from-external-files)
  - [Controlling Depth](#controlling-depth)
    - [depth: 2](#depth-2)
    - [depth: 3](#depth-3)
    - [No depth (all levels)](#no-depth-all-levels)
  - [How It Works](#how-it-works)
    - [Anchor Slugs](#anchor-slugs)
    - [Duplicate Headings](#duplicate-headings)
    - [Indentation](#indentation)
    - [Fenced Code Blocks](#fenced-code-blocks)
  - [Complete Property Reference](#complete-property-reference)
  - [Examples in This Manual](#examples-in-this-manual)

## Overview

A table of contents helps readers navigate longer documents. Maintaining one by hand is tedious and error-prone — add a section, forget to update the TOC, and it's already out of date.

EmbedM's `toc` embed type generates a table of contents automatically from markdown headings. It produces GitHub-compatible anchor links, handles duplicate headings, and stays in sync every time you compile.

Two modes are supported:
- **Current document** — generate a TOC from the headings in the same file
- **External file** — generate a TOC from a different markdown file

## Basic Usage (Current Document)

To generate a TOC from the current document's headings, use `type: toc` with no additional properties.

**Input:**
```yaml
type: toc
```

The TOC at the top of this manual is a live example — it was generated using exactly this syntax.

The generated output is a markdown list with anchor links:

```markdown
- [Overview](#overview)
- [Basic Usage (Current Document)](#basic-usage-current-document)
  - [Where to Place the TOC](#where-to-place-the-toc)
- [TOC from External Files](#toc-from-external-files)
...
```

### Where to Place the TOC

The TOC embed can appear anywhere in the document, but conventionally it goes near the top, after the title and an optional introduction. The TOC is generated during the POST_PROCESS phase, so it sees all headings in the final document — including those produced by other embeds.

## TOC from External Files

Use the `source` property to generate a TOC from a different markdown file. This is useful when you want to show the structure of a document without embedding its full content.

**Input:**
```yaml
type: toc
source: examples/toc_example.md
```

**Output:**
- [Project Overview](#project-overview)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Configuration](#configuration)
  - [API Reference](#api-reference)
    - [Endpoints](#endpoints)
      - [Authentication](#authentication)
      - [Users](#users)
  - [FAQ](#faq)

The source path is resolved relative to the markdown file containing the embed, just like `type: file` embeds.

## Controlling Depth

Use the `depth` property to limit which heading levels are included. For example, `depth: 2` includes only `#` and `##` headings, omitting deeper levels.

### depth: 2

**Input:**
```yaml
type: toc
source: examples/toc_example.md
depth: 2
```

**Output:**
- [Project Overview](#project-overview)
  - [Getting Started](#getting-started)
  - [API Reference](#api-reference)
  - [FAQ](#faq)

This is useful for top-level navigation where subsections would add too much noise.

### depth: 3

**Input:**
```yaml
type: toc
source: examples/toc_example.md
depth: 3
```

**Output:**
- [Project Overview](#project-overview)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Configuration](#configuration)
  - [API Reference](#api-reference)
    - [Endpoints](#endpoints)
  - [FAQ](#faq)

### No depth (all levels)

When `depth` is omitted, all heading levels (`#` through `######`) are included. See the full output in the [TOC from External Files](#toc-from-external-files) section above.

## How It Works

### Anchor Slugs

EmbedM generates GitHub-style anchor slugs from heading text:

| Heading | Slug |
|---------|------|
| `## Getting Started` | `#getting-started` |
| `## API Reference` | `#api-reference` |
| `## What's New?` | `#whats-new` |
| `## my_config` | `#my-config` |

The rules: lowercase, remove special characters, replace spaces and underscores with hyphens, trim leading/trailing hyphens.

### Duplicate Headings

If a document has multiple headings with the same text, EmbedM appends `-1`, `-2`, etc. to keep anchors unique:

| Heading | Slug |
|---------|------|
| First `## Example` | `#example` |
| Second `## Example` | `#example-1` |
| Third `## Example` | `#example-2` |

This matches GitHub's duplicate heading behavior.

### Indentation

Each heading level adds 2 spaces of indentation in the TOC list:

- `#` headings — no indent
- `##` headings — 2 spaces
- `###` headings — 4 spaces
- `####` headings — 6 spaces

### Fenced Code Blocks

Lines inside fenced code blocks (`` ``` ``) are skipped, even if they start with `#`. This prevents code comments from appearing as TOC entries:

````markdown
## Real Heading

```python
# This comment is NOT picked up by the TOC
## Neither is this
```

## Another Real Heading
````

Only "Real Heading" and "Another Real Heading" appear in the TOC.

## Complete Property Reference

```yaml
type: toc

# Optional - Source
source: path/to/file.md         # Generate TOC from external file (relative to current file)
                                 # If omitted, generates from current document

# Optional - Depth
depth: 2                         # Max heading level to include (e.g., 2 = # and ## only)
                                 # If omitted, all levels are included
```

## Examples in This Manual

This manual itself uses EmbedM. The table of contents at the top was generated with `type: toc`, and the external file examples use `type: toc` with `source` pointing to `examples/toc_example.md`.
