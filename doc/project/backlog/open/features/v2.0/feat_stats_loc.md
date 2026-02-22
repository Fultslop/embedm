FEATURE: Stats plugin — Lines of Code metric
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

Extend the `stats` plugin with a `loc` metric that counts non-blank, non-comment-only lines in source code files. Unlike `lines` (which counts non-empty lines in any file), `loc` is language-aware and excludes comment-only lines.

Directive definition:

```yaml embedm
type: stats
source: ./src/my_module.py
metric: loc
```

### Behaviour

- Only valid when `source` is provided (current-document mode is not meaningful for code).
- Language is inferred from the file extension.
- A line counts as code if it is non-empty after stripping leading whitespace, and is not a comment-only line.
- Single-line comment prefixes by language: `#` (Python, Ruby, Shell), `//` (JS, TS, C, C#, Java, Go, Rust), `--` (SQL, Lua), `%` (MATLAB).
- Block comments (e.g. `/* ... */`, `"""..."""`) count as zero LoC lines while open.
- Unsupported extension → falls back to `lines` metric with a note in output.
- Output: single integer, same as other `stats` metrics.

### Architecture

- Reuse language/extension detection already present in the symbol extraction infrastructure.
- Add `loc` as a branch in the stats metric dispatch, alongside `words`, `lines`, `chars`, `sentences`.
- Block comment state tracking requires a small stateful line scanner per language.

## Acceptance criteria

- Python, JS/TS, SQL files produce correct LoC for known inputs
- Comment-only lines are excluded
- Block comments are excluded
- Blank lines are excluded
- Unsupported extension falls back to `lines` with a note
- Missing `source` → error caution block
- Unit tests cover each supported language and edge cases (empty file, file with only comments)

## Comments

`22/02/2026 FS/Claude:` Deferred from v1.0. The symbol extraction infrastructure already handles language detection, making this straightforward to implement. The v1.0 `lines` metric is sufficient for Markdown and prose; `loc` is the code-specific complement.
