# Nested Layout example

```yaml
type: embed.layout
orientation: column
border: "1px #BBCCBB"
sections:
  - size: 30%
    embed:
      type: embed.file
      source: embed_layout.md
  - size: auto
    embed:
      type: embed.file
      source: lorem-ipsum.md
```