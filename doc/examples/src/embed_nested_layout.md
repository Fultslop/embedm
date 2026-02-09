# Nested Layout example

```yaml embedm
type: layout
orientation: column
sections:
  - size: 30%
    border: "1px #BBCCBB"
    embed:
      type: file
      source: embed_layout.md
  - size: auto
    border: "2px #BBCC0B" 
    embed:
      type: file
      source: lorem-ipsum.md
```