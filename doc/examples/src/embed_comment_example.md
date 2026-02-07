# Documentation with Comments

This example demonstrates how to use `embed.comment` to document your markdown structure.

```yaml
type: embed.comment
text: The following layout creates a dashboard-style view with three panels. The left panel shows a table of contents, the middle panel contains the main content, and the right panel will show related links.
```

```yaml
type: embed.layout
orientation: row
gap: 20px
padding: 20px
border: "1px solid #e0e0e0"
sections:
  - size: 20%
    background: "#f5f5f5"
    padding: 15px
    embed:
      type: embed.comment
      text: This sidebar is intentionally narrow to maximize space for content. If the TOC grows too long, consider adding overflow-y scrolling.
  - size: 60%
    padding: 20px
    background: white
    embed:
      type: embed.comment
      text: Main content area - this is where the primary documentation will be displayed once we finalize the content file.
  - size: 20%
    background: "#f9f9f9"
    padding: 15px
    embed:
      type: embed.comment
      text: Right sidebar for related links, quick references, or related resources. Consider adding a max-height with overflow if content is lengthy.
```

```yaml
type: embed.comment
text: TODO: Replace the comment placeholders above with actual content embeds once the source files are created (guide-content.md, toc-links.md, related-links.md)
```

## Additional Examples

```yaml
type: embed.comment
text: This section will contain code examples demonstrating the API. Using line_numbers: html for better readability.
```

```yaml
type: embed.comment
```

```yaml
type: embed.comment
text: The above empty comment serves as a visual separator in the source file without affecting the compiled output.
```

## Benefits

Comments are particularly useful when:

1. **Designing layouts** - Document why you chose specific sizes and arrangements
2. **Team collaboration** - Explain structure decisions to other maintainers
3. **Work in progress** - Mark sections that are incomplete or need review
4. **Complex embeds** - Add context about how nested embeds relate to each other

All comments above will be completely removed when this file is compiled with embedm.
