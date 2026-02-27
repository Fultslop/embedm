FEATURE: Add option to filter out comments
========================================
Draft
Release v1.0
Created: 26/02/2026
Closed: `<date>`
Created by: FS

## Description

The File plugin supports embedding snippets from code files (c/c++/java/c#/python). Currently this take the entire code block as-is. This includes comments, eg

```yaml embedm
type: file
source: ../../../src/embedm/domain/directive.py
symbol: Directive
```

becomes

```py
class Directive:
    type: str
    # source file, may be None if a directive does not use an input file
    # eg ToC
    source: str = ""
    options: dict[str, str] = field(default_factory=dict)
    # directory of the file that contains this directive (for relative link computation)
    base_dir: str = ""
```

The comments are quite noisy for the purpose of reading documentation and we need to filter those out if the user has set the option: `filter_comments: true` in the File Directive (filter_comments, should default to 'false'). In this case:

```yaml embedm
type: file
source: ../../../src/embedm/domain/directive.py
symbol: Directive
filter_comments: true
```

will become

```py
class Directive:
    type: str
    source: str = ""
    options: dict[str, str] = field(default_factory=dict)
    base_dir: str = ""
```

## Approach

Post-process transform (option 1 from the original discussion). The efficiency concern about double-parsing does not apply: the transformer receives the already-extracted snippet (a small block), not the full source file.

### Scope

Two tiers of comment removal are in scope:

1. **Full-line comments** — lines whose only content is a comment are dropped entirely.
   - `# comment` (Python)
   - `// comment` (C/C++/Java/C#)
   - Lines entirely within a `/* ... */` block comment

2. **Trailing inline comments** — comments that follow real code on the same line are stripped; the code is kept.
   - `x = 1; // note` → `x = 1;`
   - `x = 1  # note` → `x = 1`
   - String literals are respected: `url = "http://foo"` is not mangled.

Out of scope: mid-expression block comments (`x = /* note */ y + 1`).

### Architecture

- **`embedm/parsing/comment_filter.py`** — new module with a pure function `filter_comments(content: str, style: CommentStyle) -> str` and a private `_strip_line_comment(line, style, state) -> tuple[str | None, _ScanState]` helper. `None` return means drop the line. Uses a character-walking state machine (similar to `_scan_line` in `symbol_parser.py`) to find comment start positions while respecting string boundaries. Block-comment state (`in_block_comment`) is tracked across lines.

- **`embedm_plugins/file/comment_filter_transformer.py`** — new `CommentFilterTransformer` with `CommentFilterParams(content: str, style: CommentStyle)` and `execute() -> str`, wrapping `filter_comments`. Follows the existing transformer pattern.

- **`file_plugin.py`** — reads the `filter_comments` boolean option. If `True`, invokes `CommentFilterTransformer` on the extracted content (after `_apply_extraction`, before the fenced block is built). Requires `get_language_config` to succeed; if the source extension has no language config, the option is silently ignored (the plugin already prevents `symbol` on unsupported extensions; `filter_comments` alone is benign to ignore).

- **`validate_directive`** — no new validation required. `filter_comments` is valid on any extraction mode (region, lines, symbol) and any supported extension.

## Acceptance criteria

- `filter_comments: true` on a Python snippet removes full-line `#` comments and strips trailing `# ...` from code lines.
- `filter_comments: true` on a C/C++/C#/Java snippet removes full-line `//` comments, full `/* ... */` blocks, and strips trailing `// ...` from code lines.
- String literals containing comment-like sequences (`"http://foo"`, `"{"`) are not mangled.
- `filter_comments: false` (default) produces identical output to the current behaviour.
- `filter_comments: true` on a source with an unsupported extension is flagged as a warning during the `validate_directive` step in FilePlugin. (content unchanged).
- The option works with all extraction modes: no option (whole file), `symbol`, `region`, `lines`.
- Blank lines that result from removing a comment-only line are not added; the dropped line simply disappears.

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
