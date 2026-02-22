FEATURE: Query plugin — directory source
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS/Claude

## Description

Extend the query plugin (`type: json | yaml | xml`) to accept a directory as its `source`, normalizing the file system structure into the query pipeline's internal tree so that file and directory properties can be embedded using the same dot-notation path syntax as data files.

Depends on: `feat_json_plugin.md` (query plugin v1.0 must be implemented first).

Related: `feat_directory_plugin.md` (v1.0) covers tree *visualization* from a directory source using `type: directory`. This feature covers property *querying* — e.g. embedding a specific file's size or last-modified date — using the shared normalize/query pipeline.

Directive example:

```yaml embedm
type: json
source: ./src
path: embedm.plugin_base.size
```

### Behaviour

- When `source` resolves to a directory, a directory normalizer is used instead of a data-file parser.
- The normalized structure maps directory and file nodes to a queryable tree (see normalization proposal in `feat_json_plugin.md` comments).
- File properties exposed per node: `size`, `last_modified`, `permissions` (platform-dependent).
- Scalar property → plain inline text. Subtree → fenced code block. Consistent with v1.0 presenter behaviour.
- Path not found → error caution block.

### Architecture

- Add `normalize_directory.py` alongside `normalize_json.py`, `normalize_yaml.py`, `normalize_xml.py`.
- Query engine and presenter are unchanged — the normalizer output is the same internal tree type.
- Source-type dispatch (file vs. directory) happens in the plugin's validate step before the query engine is invoked.

## Acceptance criteria

- DISCUSS

## Comments

`22/02/2026 FS/Claude:` Deferred from feat_json_plugin.md v1.0. Directory traversal requires OS calls and a property model with no equivalent in JSON/YAML/XML, making it a poor fit for the initial release. The normalize/query/present pipeline generalizes to cover it cleanly once the core is stable.
