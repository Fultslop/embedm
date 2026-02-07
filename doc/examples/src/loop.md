# loop protection - the following embeddings should yield a warning

## loop via parent

```yaml
type: embed.file
title: cannot include parent
file: ./include_loops.md
```

## loop via self

```yaml
type: embed.file
title: cannot include self
file: ./loop.md
```