# Embedm backlog

## Planned

* File properties, region, line, symbol
* Review, check if we can/need to move functionality from table transformer to other file. 
  * Opportunity to have transformer chaining ?
  * Note that table_transformer contains hard coded strings again.
  * Magic consts again:
      if ext == "csv":
        return _parse_delimited(content, ","), None
      if ext == "tsv":
        return _parse_delimited(content, "\t"), None
      if ext == "json":
        return _parse_json(content)
  => turn into a function map
  * Comments should capture intention. Guess it's hard to determine when it's needed and not
    eg. _parse_delimited
    * Error handlig is not using the status pattern established elsewhere
      eg: def _parse_json(content: str) -> tuple[list[Row], str | None]:
      try:
          data: Any = json.loads(content)
      except json.JSONDecodeError as exc:
          return [], _render_error(str_resources.err_table_invalid_json.format(exc=exc))
    * Avoid using unicode chars, prefer '->' over '→' in docs

* --silent --dry-run --verify
* Add progress indicator

**Design / speculation**

* Plugin sequence (`config.plugin_sequence`) is parsed and stored but never used to filter
  `load_plugins()` — the TODO has been there a while. Consider whether the feature is still wanted
  or should be removed to avoid misleading config.

* Good design question. Here's my read on where the scope boundary should sit.

Safe to add — well-defined parsing, no ambiguity:

limit / offset: trivial list slicing, no parsing
select: split on commas, handle col as alias with a single regex — clear input format, clear failure mode
order_by: split on commas, split each part by space to get (column, asc|desc) — same story
Where I'd be cautious — the where string:

The risk isn't the initial implementation, it's the contract. The moment you accept a free-form string, users will write whatever they'd write in SQL and expect it to work. You'll get bug reports for:

OR logic
LIKE/IN/BETWEEN
type coercion edge cases ("24" vs 24)
parentheses / operator precedence
escaped quotes in string values
There's no natural stopping point once you've accepted a string parser.

What I'd suggest instead — structured filtering:


type: table
source: some_file.csv
select: "column_x, column_y as y"
order_by: "y desc"
limit: 10
offset: 20
filter:
  column_x: "value"    # exact match
  y: "<= 24"           # operator + literal
A filter mapping where each value is either a bare literal (exact match) or "op literal" where op is one of =, !=, <, <=, >, >=. Multiple keys are implicitly ANDed.

This gives you explicit scope: you support exactly these operators, one condition per column, no OR, no nesting. Users who need something more complex can pre-filter their CSV. The failure mode is also clean — an unrecognised operator string returns an error Status rather than silently misfiltering.

On IS NULL: I'd skip it for now or handle it as a special string "is null" / "is not null" if it comes up. Most table sources from real CSVs represent nulls inconsistently anyway.

The short version: select, limit, offset, order_by — yes. where as a string — replace with a structured filter map with a fixed operator vocabulary. That gives familiar semantics, a hard scope boundary, and no parser to maintain.

Ah, column data types for rendering — different question.

The safe ones (handle directly):

string, int, bool: str() and done
decimal/float: expose a precision option for formatting, otherwise str() is fine
date/datetime: expose a date_format option using strftime — very common need, low cost
null: expose a null_string option (default empty, could be - or N/A)
The gnarly ones:

JSONB: the content is renderable (it's just a string in the source), but the output is unreadable — a cell containing {"status": "active", "meta": {"created": ...}} breaks the table visually. Don't try to be clever here — just apply truncation and let the user exclude the column via select if they don't want it.

MediaTypes as MIME strings (image/jpeg): fine, just strings. If you mean actual binary content, that should never reach the table renderer — it means the export itself was wrong.

Arrays (Postgres {1,2,3}, JSON [1,2,3]): same as JSONB — stringify and truncate.

Binary/bytea: render as [binary] and move on. No value in trying to display it.

The practical approach: one option covers most of it

A max_cell_length option (default say 80 chars) that truncates all values with ... handles JSONB, long strings, arrays, and anything else gnarly in one shot. That's less design surface than per-type formatting rules and solves the visual corruption problem.

So the full options surface ends up being:


select: "col_a, col_b as b"
order_by: "b desc"
limit: 10
offset: 0
date_format: "%Y-%m-%d"    # applied to date/datetime values
null_string: "-"            # what to render for nulls
max_cell_length: 80         # truncates anything longer
Anything that doesn't fit renders as a truncated string. The user excludes columns they can't handle via select. That's a complete, bounded contract with no gnarly type-specific code paths.

## Done

* Enabled plugins -> should be covered by plugin sequence ?
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

* `get_option` return type (`T | Status | None`) forces callers to assert the type after the call
  to satisfy mypy. Overloading or a two-step validate/get pattern would be cleaner and remove the
  runtime asserts-for-types pattern that is currently needed.

* `find_yaml_embed_block` returns `None` silently for unclosed fences; `_find_all_raw_blocks`
  returns an explicit error `Status`. Inconsistent contract for the same underlying problem.

* Collect user facing strings - they sit in resources now

* * def load_plugins(self, enabled_plugins: set[str] | None = None, verbose: bool = False) -> None:
  hides failure to load plugins come up with a proposal and implement

* --accept-all -A

* Setup regression testing

* Create table_reader transformer
* Create table_converter transformer
* Create table_plugin
* Table plugin with sql-ish syntax
