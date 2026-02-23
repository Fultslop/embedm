# Agent Context

This document is compiled from project sources to give Claude focused context at session start.
Read this before beginning any task. It does not replace the files it draws from — go to the source
for full detail.

## Project guidelines

```yaml embedm
type: file
source: ./guidelines.md
```

## Plugin conventions

Key decisions about plugin structure, registration, and naming extracted from the decision log.

```yaml embedm
type: recall
source: ./devlog.md
query: "plugin entry point resource naming convention registration sequence"
max_sentences: 5
```

## Architectural rules

Core rules about the validation/transform boundary, error handling, and code quality.

```yaml embedm
type: recall
source: ./devlog.md
query: "transformer pure validation separation boundary coding errors assert"
max_sentences: 5
```

## Patterns — avoid these misses

Established patterns that have caused errors when overlooked. Check these before writing any embed directive or adding a plugin.

```yaml embedm
type: recall
source: ./devlog.md
query: "missed pattern established embed dynamic hardcoded query-path"
max_sentences: 4
```

## Active feature spec

implement `doc_document_query_path_plugin.md` in `doc\project\backlog`.

If you can't find this because the active spec may be moved or renamed, ask the user.