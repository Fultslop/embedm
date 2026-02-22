FEATURE: Query plugin — glob path queries
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS/Claude

## Description

Extend the query plugin (`type: json | yaml | xml`) with glob-style path expressions that can match multiple nodes in a single query. The primary use case is extracting lists of values or structured subsets from a document rather than a single scalar.

Depends on: `feat_json_plugin.md` (query plugin v1.0 must be implemented first).

Directive definition:

```yaml embedm
type: json
source: ./package.json
path: dependencies/**
output: key          # key | value (default)
format: list         # list (default) | tree
recursive_depth: 2
```

### Behaviour

- `path` may contain `*` (single segment wildcard) or `**` (recursive descent).
- When a glob path matches multiple nodes, results are aggregated.
- `output: key` emits the matched key names; `output: value` (default) emits the matched values.
- `format: list` emits a markdown list; `format: tree` emits a fenced code block preserving structure.
- `recursive_depth` caps descent when `**` is used; default matches the global `max_recursion` config.
- A glob that matches zero nodes → error caution block.
- A non-glob path falls back to v1.0 single-node behaviour (no regression).

### Architecture

- Extend the shared query engine from `feat_json_plugin.md`; normalizers are unchanged.
- Path parser distinguishes glob from dot-notation at directive validation time.
- Result aggregation and formatting are a new presenter layer alongside the existing scalar/dict/list presenter.

## Acceptance criteria

- DISCUSS

## Comments

`22/02/2026 FS/Claude:` Deferred from feat_json_plugin.md v1.0. Single dot-notation paths cover the primary use case (config values, version numbers). Glob queries require a result-aggregation model and output format options that are out of scope for the initial release.
