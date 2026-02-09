# loop protection - the following embeddings should yield a warning

## loop via parent

```yaml embedm
type: file
title: cannot include parent
source: ./embed_loops.md
```

## loop via self

```yaml embedm
type: file
title: cannot include self
source: ./loop.md
```