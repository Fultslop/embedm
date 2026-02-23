BUG: Recall captures absolute paths
========================================
Created: 23/02/2026
Closed: `<date>`
Created by: FS


## Description

In `doc\project\agent_context.src.md` a relative path to a spec the backlog was captured (removed since). ie:

````md
## Active feature spec

```yaml embedm
type: file
source: ./backlog/in_progress/feat_agent_context_document.md
```
````

The problem is that these specs move around in the backlog depending on their status. (Discuss) It might be better to capture the active feature as 'last feature worked on' (or something to that effect) and a file name (feat_agent_context_document.md) which can be found dynamically. If the file can't be found (because it could be renamed or removed), the agent could ask the user.


## Replication

**Input:**

Active feature was added to the agent context. Not clear where / how. This was the agent_context src:

````md
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

```yaml embedm
type: file
source: ./backlog/in_progress/feat_agent_context_document.md
```

````

**Output**

Compiled active feature refers to a file that doesn't exist on that path. File too large to add here.

**Expected**

(Discuss) It might be better 

1) to capture the active feature as 'last feature worked on' (or something to that effect) and only the file name (`feat_agent_context_document.md`) + the parent directory, in this case `./doc/project/backlog` which can be resolved dynamically . 

2) If the file can't be found (because it could be renamed or removed), the agent could ask the user.
