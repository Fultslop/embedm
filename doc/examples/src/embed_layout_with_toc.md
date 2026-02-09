# Documentation with Sidebar TOC

This example demonstrates a layout with a scrollable table of contents sidebar that references another file.

```yaml embedm
type: layout
orientation: row
gap: 20px
padding: 20px
border: "1px solid #e0e0e0"
background: "#fafafa"
comment: "Two-column layout: fixed-width TOC sidebar (250px) + flexible content area"
sections:
  - size: 250px
    max-height: 600px
    overflow-y: auto
    overflow-x: hidden
    padding: 15px
    border: "1px solid #ddd"
    background: "#f8f9fa"
    embed:
      type: toc
      source: guide-content.md
  - size: auto
    padding: 15px
    background: white
    embed:
      type: file
      source: guide-content.md
```

The TOC sidebar:
- Has a fixed width of 250px
- Scrolls when content exceeds 600px height
- References `guide-content.md` using the `source` property
- Matches the content displayed in the main section
