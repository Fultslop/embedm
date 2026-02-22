TECHNICAL IMPROVEMENT: Fix compilation to multi-pass DFS ordered by plugin_sequence
========================================
Created: 21/02/26
Closed: 22/02/26
Created by: Claude

## Description

`FileTransformer.execute` in `src/embedm_plugins/file_transformer.py` compiles a document
in a **single left-to-right pass**, calling whichever plugin handles each directive type
as it is encountered in document order. `plugin_sequence` is only used at startup to load
plugin modules; it plays no role in compilation order.

The intended architecture is **multi-pass DFS**:

```
compile(document, plugin_sequence):
    for plugin_type in plugin_sequence:
        for each directive of plugin_type in document:
            if plugin_type == "file":
                result = compile(child_document, plugin_sequence)  # DFS
            else:
                result = plugin.transform(...)
            replace directive with result string
```

Pass 1 (`file_plugin`) fully resolves all embedded content recursively before any other
plugin runs. By the time `toc_plugin` runs (pass 3 by default), every embedded file is
already compiled text. A `{{ toc }}` placed at the top of a document would correctly
include headings from files embedded below it.

**Current behaviour (bug):** `plugin_sequence` has no effect on compilation order. All
directive types are compiled in document order in a single pass. A `{{ toc }}` placed
before a `{{ file source: chapter.md }}` directive will miss all headings in `chapter.md`.
This is also the blocking issue for the Synopsis plugin, which requires the same compiled
document view.

**Note on the `parent_document` parameter:** The `parent_document` list currently passed
to each plugin's `transform()` is the *original unresolved* fragment list (with `Directive`
objects). With multi-pass compilation, each pass replaces `Directive` objects with compiled
strings, so by the time a later-pass plugin runs, `parent_document` is a list of strings —
no further changes to the `parent_document` contract are needed.

**Files affected:**

- `src/embedm_plugins/file_transformer.py` — `_resolve_directives` becomes a loop over
  the ordered plugin type list; `_transform_directive` receives the current plugin type to
  filter on.
- `src/embedm/plugins/plugin_configuration.py` — add `plugin_sequence: list[str]` field
  so the ordered directive-type list can be threaded through `transform()` calls into the
  recursive `FileTransformer.execute`.
- `src/embedm/application/orchestration.py` — build the ordered type list from the
  registry before calling `_compile_plan_node` and pass it in via `PluginConfiguration`.
- `tests/embedm_plugins/file_transformer_test.py` — update and add tests for multi-pass
  behaviour.
- `tests/regression/` — any regression document with `{{ toc }}` placed *before* a
  `{{ file }}` embed will produce different (now correct) output; those fixtures must be
  reviewed and updated.

## Acceptance criteria

* A document with `{{ toc }}` at the top and `{{ file source: chapter.md }}` below it
  produces a ToC that includes all headings from `chapter.md`.

* A document with nested file embeds (A embeds B which embeds C) compiles all of C before
  B's other directives run, and all of B before A's other directives run (DFS order).

* `plugin_sequence` order is respected: in a document that mixes `file` and `table`
  directives, all `file` embeds are fully resolved before any `table` directive is
  processed.

* All existing regression tests that are not affected by the ToC-ordering fix continue
  to pass unchanged.

* Regression tests that previously had incorrect ToC output (missing headings from embeds)
  are updated to reflect the now-correct output.

## Comments

**21/02/26 Claude:**

The comment on `file_transformer.py:44` reads `# DFS — children compiled on demand`.
The DFS recursion is present (a `file` directive does recurse into the embedded file), but
the full `plugin_sequence` pipeline is not applied at each level. The fix does not change
the DFS structure, only ensures that at each level all passes run in `plugin_sequence` order
before returning to the parent.

The `plugin_configuration.py` change is the mechanical thread-through. An alternative
is to pass the ordered type list as a separate parameter, but using `PluginConfiguration`
keeps it consistent with how `max_recursion` and `compiled_dir` are already threaded.
