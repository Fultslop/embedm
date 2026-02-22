FEATURE: Stats plugin
========================================
Draft
Release v1.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

A plugin that computes and embeds simple metrics about a file or the current document: word count, line count, character count, sentence count. Output is plain inline text (a single number) or a formatted summary line.

Useful for README files that advertise document size, audit reports, and living documentation that tracks its own completeness.

Directive definition:

```yaml embedm
type: stats
source: ./large_manual.md   # optional — defaults to current document
metric: words               # words | lines | chars | sentences
```

### Behaviour

- `metric` selects which value to output. Default: `words`.
- Without `source`, the plugin operates on the current document text (the parent_document at transform time — post-embed, so embedded content is included in the count).
- Output is a single integer as plain text with no trailing newline, suitable for embedding inline: "This manual contains {words} words."
- An optional `format` option wraps the number in a sentence: `format: "{value} words"`.

Supported metrics:
| metric      | definition                                      |
|-------------|------------------------------------------------|
| `words`     | whitespace-separated token count                |
| `lines`     | non-empty line count                            |
| `chars`     | character count excluding whitespace            |
| `sentences` | sentence count (same splitter as synopsis)      |

### Architecture

- Runs after the `file` pass so embedded content is counted.
- No external dependencies.
- Text extraction: same approach as synopsis plugin (source file or parent_document fragments).

## Acceptance criteria

- Each metric produces the correct integer for a known input
- Inline embedding works (no leading/trailing whitespace in output)
- `format` option substitutes `{value}` correctly
- Source file and current-document modes both work
- Unit tests cover all four metrics and edge cases (empty document, single word)
- Regression example included

## Comments

`22/02/2026 FS/Claude:` Simple but commonly needed. Especially useful when combined with the `json` plugin: you could embed both the version and the documentation word count in a README header.

`22/02/2026 FS:` Can we extend this to LoC counts for code ? Or maybe a v2.0 feature?

`22/02/2026 FS/Claude:` Deferred to v2.0 as `feat_stats_loc`. True LoC (excluding blank and comment-only lines) requires language detection — but the symbol extraction infrastructure already handles this, so the implementation cost is lower than it appears. Not worth bloating the v1.0 stats plugin for a code-specific use case.
