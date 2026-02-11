# Layout Embedding Manual

This manual covers layout embedding in EmbedM — arranging embedded content in multi-column or multi-row arrangements using flexbox.

## Table of Contents

```yaml embedm
type: toc
```

## Important: Use With Care

> [!WARNING]
> Layout embeds produce raw HTML with inline CSS styles. This works well when rendering to HTML, but adds significant noise to the Markdown source. If your documentation is primarily read as Markdown (e.g., on GitHub), layouts may hurt readability more than they help.
>
> Consider whether a simpler approach — separate sections, tables, or side-by-side code blocks — achieves the same goal without the HTML overhead.

## Overview

The `layout` embed type arranges multiple embedded contents side by side (rows) or stacked (columns) using CSS flexbox. Each section can contain any embed type — files, tables, TOCs, or even nested layouts.

## Basic Row Layout

Place two code files side by side:

**Input:**
```yaml
type: layout
orientation: row
gap: 20px
sections:
  - size: 50%
    embed:
      type: file
      source: examples/basic_example.py
      lines: 1-5
  - size: 50%
    embed:
      type: file
      source: examples/regions_example.py
      lines: 1-5
```

This produces a flex container with two 50%-width columns separated by a 20px gap. Each column contains the embedded file content wrapped in `<div>` tags.

## Column Layout

Stack sections vertically using `orientation: column`:

```yaml
type: layout
orientation: column
gap: 10px
sections:
  - embed:
      type: file
      source: code.py
  - embed:
      type: table
      source: data.csv
```

## Sections

Each entry in `sections` is a dictionary with:

- **embed** (required) — the embed to render (any valid embed type with its properties)
- **size** (optional) — CSS width/height: `"50%"`, `"300px"`, or `"auto"` (default)

Per-section styling is also available:

| Property | Example | Description |
|----------|---------|-------------|
| `size` | `50%` | Section width (row) or height (column) |
| `border` | `1px solid #ccc` | CSS border (or `true` for default) |
| `padding` | `10px` | CSS padding |
| `background` | `#f6f8fa` | CSS background color |
| `overflow` | `auto` | CSS overflow |
| `max-width` | `400px` | Maximum width |
| `max-height` | `300px` | Maximum height |

## Container Properties

These apply to the outer flex container:

| Property | Default | Description |
|----------|---------|-------------|
| `orientation` | `row` | `row` (side by side) or `column` (stacked) |
| `gap` | `0` | Space between sections |
| `border` | — | CSS border |
| `padding` | — | CSS padding |
| `background` | — | CSS background |
| `overflow` | — | CSS overflow |
| `max-width` | — | Maximum width |
| `max-height` | — | Maximum height |
| `min-width` | — | Minimum width |
| `min-height` | — | Minimum height |

## Complete Property Reference

```yaml
type: layout

# Optional - Container
orientation: row              # "row" (side by side) or "column" (stacked)
gap: 20px                     # Space between sections
border: 1px solid #ccc        # CSS border (or "true" for default)
padding: 10px                 # CSS padding
background: "#f6f8fa"         # CSS background

# Required - Sections (at least one)
sections:
  - size: 50%                 # Section size (optional, default: auto)
    border: true              # Per-section border (optional)
    padding: 10px             # Per-section padding (optional)
    embed:                    # The embedded content (required)
      type: file
      source: path/to/file
```

## What the Output Looks Like

Layout embeds produce HTML like this:

```html
<div style="display: flex; flex-direction: row; gap: 20px;">
  <div style="flex: 0 0 50%;">
    <!-- embedded content here -->
  </div>
  <div style="flex: 0 0 50%;">
    <!-- embedded content here -->
  </div>
</div>
```

This renders correctly in HTML viewers but appears as raw HTML when viewing the Markdown source directly.
