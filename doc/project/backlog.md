# Embedm backlog

## Planned

* Collect user facing strings
* --yes-to-all
* Setup regression testing
* Table plugin with sql-ish syntax
* File properties
* --silent --dry-run --verify
* Enabled plugins -> should be covered by plugin sequence ?
* Add progress indicator

## Review findings (18/02/26)

**Bugs**

**Code quality**

* `_expand_directory_input` (orchestration.py): glob base extraction uses fragile string
  replacement (`replace("/**", "")`) rather than proper path parsing. Would break on patterns like
  `src/**/docs/*.md`.

* `find_yaml_embed_block` returns `None` silently for unclosed fences; `_find_all_raw_blocks`
  returns an explicit error `Status`. Inconsistent contract for the same underlying problem.

**Design / speculation**

* Plugin sequence (`config.plugin_sequence`) is parsed and stored but never used to filter
  `load_plugins()` — the TODO has been there a while. Consider whether the feature is still wanted
  or should be removed to avoid misleading config.

* `get_option` return type (`T | Status | None`) forces callers to assert the type after the call
  to satisfy mypy. Overloading or a two-step validate/get pattern would be cleaner and remove the
  runtime asserts-for-types pattern that is currently needed.

## Done

* ToC plugin
* Discuss IoC
* Integration tests
* Review
  * Fix duplicate source in child lookup (data loss bug)
  * Make transformer failures loud (raise on programming errors)
  * Standardise path handling on pathlib
  * Add plugin load error handling
  * Write 3-4 integration tests for the happy path
  * Stop mutating directives in-place
  * Add error channel to compilation result
* Error handling pass, user interaction
  * add tests for regression testing
* Orchestration add InputMode.DIRECTORY, InputMode.STDIN

* `toc_transformer._parse_str_fragment` returns `note_no_toc_content` for fragments with no
  headings, which gets mixed into valid TOC entries when a document has multiple string fragments
  after the directive (e.g. a trailing text section with no headings). The note should only appear
  when the entire output is empty.

* `toc_transformer.execute`: `_index` in `for _index, fragment in enumerate(...)` is unused —
  should just be `for fragment in ...`.

* `toc_transformer._parse_str_fragment`: `if max_depth is not None` is a dead check — `max_depth`
  is typed `int` and asserted as such before the call.

  * Memory limit can be exceeded: `file_cache._make_room` loops until it cannot evict further, then
  breaks and loads the file anyway. A single file larger than `memory_limit` (but within
  `max_file_size`) will silently exceed the memory budget.

* Boolean option casting: `directive_parser` converts all option values to `str` at parse time
  (`str(v)`). This means a YAML native bool (`add_slugs: true`) becomes the string `"True"`.
  `get_option(cast=bool)` must then handle `"True"`/`"False"` strings — worth verifying this
  round-trip is actually tested.

