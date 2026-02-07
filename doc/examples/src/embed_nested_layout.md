# Nested Layout example

```yaml
type: embed.layout
orientation: column
sections:
  - size: 30%
    border: "1px #BBCCBB"
    embed:
      type: embed.file
      source: embed_layout.md
  - size: auto
    border: "2px #BBCC0B" 
    embed:
      type: embed.file
      source: lorem-ipsum.md
```