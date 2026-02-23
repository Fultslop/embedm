BUG: `_clean_text mangles snake_case identifiers in recall output`
========================================
Created: 23/02/2026
Closed: `<date>`
Created by: Claude


## Description

`_clean_text` in `embedm_plugins/text_processing.py` strips underscores from
`snake_case` identifiers when they appear in the source text. For example,
`plugin_resources.py` becomes `pluginresources.py` in recall output, and
`DEFAULT_PLUGIN_SEQUENCE` becomes `DEFAULTPLUGIN_SEQUENCE`.

The recall plugin passes all source text through `_clean_text` before scoring.
The mangling happens there, so the affected sentences are stored without
underscores and the blockquote output reflects the mangled form.

Related: `embedm_plugins/text_processing.py` — `_clean_text()`

## Replication

**Input:**

A source document (e.g. `devlog.md`) containing a line such as:

```
* 22/02/26 [TASK] Refactor embedm_plugins — split monolithic plugin_resources.py into five per-plugin resource files (file_resources, query_path_resources, synopsis_resources, table_resources, toc_resources)
```

Recall directive over that document with any query that scores this sentence.

**Output**

The blockquote contains:

```
Refactor embedmplugins — split monolithic pluginresources.py into five per-plugin resource files (fileresources, querypathresources, synopsisresources, tableresources, tocresources)
```

Underscores between words are removed and the flanking word fragments are concatenated.

**Expected**

Underscores that are part of identifiers (surrounded by word characters on both sides)
should be preserved. The output should read:

```
Refactor embedm_plugins — split monolithic plugin_resources.py into five per-plugin resource files (file_resources, query_path_resources, synopsis_resources, table_resources, toc_resources)
```

## Root cause

`_clean_text` removes markdown italic syntax using:

```python
text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
```

The `.*?` (non-greedy) matches across word boundaries when multiple underscores
appear on the same line. For a line containing `plugin_resources.py ... file_resources`,
the regex matches `_resources.py ... file_` as a single italic span and collapses it,
concatenating the flanking tokens.

**Fix candidates:**

1. Use a negative lookbehind/lookahead to exclude underscores flanked by `\w` on both
   sides: `(?<!\w)_{1,3}(.*?)_{1,3}(?!\w)`
2. Restrict `.*?` to non-underscore characters for the inner span.
3. Process italic removal line-by-line to prevent cross-boundary matching.
