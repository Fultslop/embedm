# Dev Log

This document contains entries related to the work done or decisions on feature, architecture, implementation or code / design philosophy.

## Entries

* 21/02/26 [TASK] tech_fix_compilation_to_multi_pass_dfs — `FileTransformer._resolve_directives` now runs one pass per directive type following `plugin_sequence` order. `PluginConfiguration` gets a `plugin_sequence: tuple[str, ...]` field. `orchestration._build_directive_sequence` maps module names to directive types and threads the ordered tuple into `PluginConfiguration`. Recursive (DFS) calls inherit the same sequence. Single-pass fallback when `plugin_sequence` is empty (unit tests). Regression snapshot for `toc_example` requires user update.

* 21/02/26 [REVIEW] tech_fix_compilation_to_multi_pass_dfs — The existing single-pass DFS produced correct output only by accident: all current regression documents have `{{ toc }}` placed after `{{ file }}` embeds. The `plugin_sequence` field was used only to filter module loading, never to order compilation. The fix is minimal: add a `directive_type` filter param to `_resolve_directives`, wrap in a `_compile_passes` loop, thread the ordered type list via `PluginConfiguration`.

* 21/02/26 [TASK] tech_config_value_range_validation — add per-field range checks in `_parse_config()` after type validation: `max_file_size >= 1`, `max_recursion >= 1`, `max_embed_size >= 0`. Each yields ERROR and returns default `Configuration()`. Consolidated alongside the existing `max_memory > max_file_size` cross-field check. Error messages added to `application_resources.py`.

* 21/02/26 [TASK] tech_fix_path_boundary_check_in_file_cache — replace bare `startswith` in `_is_path_allowed()` with `Path.relative_to()`. Adjacent directories (e.g. `project_evil` when `project` is allowed) are now correctly rejected. Adds three acceptance-criteria tests.

* 21/02/26 [REVIEW] tech_fix_path_boundary_check_in_file_cache — `startswith` is a string prefix check, not a directory boundary check. `Path.relative_to()` is the correct stdlib idiom: it raises `ValueError` for adjacent siblings and succeeds for exact matches and subdirectories. The spec proposes a manual separator check; `relative_to` is simpler and more idiomatic.

* 21/02/26 [REVIEW] tech_move_validation_from_table_transformer_execute — pipeline steps (_apply_select, _apply_order_by) currently return errors via CAUTION strings; for the transformer to be fully pure, column/expression validation must also move to validate_input. validate_input will run _parse_content + validate select columns + validate order_by expressions, returning rows as artifact. The transformer becomes error-free: asserts for programming violations, note_no_results for empty-after-filtering.

* 21/02/26 [TASK] tech_move_validation_from_table_transformer_execute — ValidationResult[TArtifact] wrapper in validation_base.py; PlanNode.artifact: Any = None; PluginBase.validate_input() no-op default; planner calls validate_input after file is cached, stores artifact on child node; CsvTsvTableValidation and JsonTableValidation in table_validation.py; TableParams.rows replaces content/file_ext; TableTransformer.execute() is pure; table_plugin.py overrides validate_input and reads artifact in transform.

* 21/02/26 [Fix] Bug: symbols inside comments are parsed — `_find_symbol_in_range` now always calls `_scan_line` to strip comments, and `_try_match_at_line` matches against the comment-stripped line instead of the raw line. Covers both `/* */` block comments and `//` line comments for all supported languages (C/C++, C#, Java).

* 21/02/26 [Fix] Bug: compiled file link does not resolve — `link: true` in the file plugin now emits a path relative to the compiled output directory instead of the source md directory. `compiled_dir` added to `PluginConfiguration` and threaded from orchestration through `_compile_plan_node` → `plugin.transform()` → `FilePlugin` → `_build_header`. `FileParams` carries `plugin_config`. Falls back to filename when `compiled_dir` is unset (stdin/stdout mode).

* 20/02/26 [Feat] File plugin header decorators — `title` (bold label), `link: true` (filename as link), `line_numbers_range: true` (shows `lines` value when present). Rendered in order title → line_numbers_range → link as a single line above the code block. Uses `Directive.get_option` for bool casting.

* 20/02/26 [Fix] Symbol parser: qualified lookup (e.g. `Example.doSomething()`) now restricts to direct members of the narrowed scope using brace-depth tracking, fixing inner-class name collision bug.

* 20/02/26 [Feat] File extraction — region (md.start/end markers), line range (..), symbol (C/C++, C#, Java: namespace/class/struct/enum/interface/function/method). Pipeline: FileTransformer compiles, extraction transformers post-process. Non-markdown sources wrapped in fenced code block.



* 19/02/26 [Arch] Plugin output size enforcement — `max_embed_size` is now enforced post-transform in `file_transformer._transform_directive()`. Exceeding the limit replaces the directive output with a caution block. `FileCache` is the chosen carrier for the limit (it already owns `max_file_size` and `memory_limit`), threaded from config via `orchestration._build_context()`. Value 0 disables enforcement. In-transform memory consumption (allocations before `transform()` returns) cannot be enforced in pure Python without OS-level process isolation; this is an accepted limitation. The plugin trust model relies on users controlling `plugin_sequence` in their config.

* 19/02/26 [Feat] Table plugin — renders CSV, TSV, and JSON as markdown tables. Options: select (column projection with AS aliases), filter (structured conditions per column: exact match or op literal where op ∈ {=, !=, <, <=, >, >=}, ANDed), order_by (multi-column, asc/desc), limit, offset, date_format, null_string, max_cell_length. Nested YAML filter map serialized as JSON via a `_to_option_str` hook in the directive parser.

* 19/02/26 [Feat] Accept-all prompt option — interactive 'a'/'always' choice in the continue prompt persists across files in a directory run. `-A`/`--accept-all` CLI flag pre-sets this. Errors always shown; fatal errors still halt. `ContinueChoice` enum replaces the bool return from `prompt_continue`.

* 19/02/26 [Arch] Plugin load failures treated as user errors — `load_plugins` now returns `list[Status]` and catches per-entry exceptions gracefully. Errors are surfaced via `present_errors` in orchestration but processing continues. Missing plugins fall through to the existing "no plugin registered" document error path.

* 16/02/26 [Feat] Directory mode — `embedm .` (non-recursive), `embedm ./*` (non-recursive), `embedm ./**` (recursive). Processes all .md files, skipping files already embedded as dependencies via plan tree walk. Auto-detects directory/glob inputs. `-o` blocked for directory input; `-d` writes to output directory.

* 16/02/26 [Feat] Config file support — `--init [path]` generates `embedm-config.yaml` with commented defaults, `--config` loads explicit config, auto-discovers config in input file's directory. Precedence: --config > auto-discovered > defaults.

* 16/02/26 [Arch] Move root directive type from hardcoded constant in planner to `root_directive_type` config — eliminates planner's implicit dependency on the file plugin

* 16/02/26 [Feat] Interactive continue/abort prompt in orchestration — after planning, tree errors are collected and presented, user can continue (errors render as Note blocks) or abort. Respects is_force_set and FATAL errors.

* 16/02/26 [Feat] Error directives render as GFM `> [!CAUTION]` blocks during compilation — unknown plugins, unbuildable sources, and error nodes produce visible markers instead of silent empty output

* 16/02/26 [Code] Planner collect-and-continue — always builds document and children, collects all errors without short-circuiting. Orchestration uses tree-wide error collection instead of document-is-None check.

* 16/02/26 [Code] Assert preconditions at pipeline boundaries — transformer asserts document/source cached, plugin asserts file_cache/plugin_registry provided. Coding errors crash fast per error-handling guidelines.

* 16/02/26 [Standards] Error handling guidelines — coding errors crash via assert, input errors collect Status and recover. Boundary rule: if a user could cause it via bad markdown or args, it's an input error. See doc/project/error-handling.md

* 16/02/26 [Task] Add integration tests in tests/integration/ — full pipeline (file → parse → plan → compile → output) with real plugins, no mocks

* 16/02/26 [Arch] No IoC container — project scale doesn't justify the abstraction overhead. Plugin system already provides IoC via entry points. Revisit if plugin construction needs injected dependencies.

* 16/02/26 [Code] Move relative path resolution from planner into parser via base_dir param — directives now store absolute paths from creation

* 16/02/26 [Code] Standardize path handling on pathlib, remove os.path usage from planner and parser

* 16/02/26 [Code] Convert Document to @dataclass, TransformerBase.execute to @abstractmethod

* 16/02/26 [Code] Replace hardcoded version string with importlib.metadata.version()

* 16/02/26 [Standards] Add TODO for transformer child_lookup dict losing duplicate same-source directives

* 15/02/26 [Task] Wire up orchestration with CLI, planner, plugin dispatch, and output writing for FILE mode

* 15/02/26 [Feat] Implement CLI argument parser with argparse — supports file, directory, stdin input modes and output options

* 15/02/26 [Code] Convert Configuration to @dataclass with sensible defaults for limits and plugin sequence

* 15/02/26 [Arch] Replace compiler with embedm_file_plugin — all document compilation logic lives in the plugin, no separate compiler needed

* 15/02/26 [Arch] Root PlanNode uses embedm_file directive type so orchestration just dispatches to the plugin registry

* 15/02/26 [Task] Implement compiler with DFS plan traversal, span resolution, and ordered plugin passes

* 15/02/26 [Task] Implement planner with directive validation, recursion control, and tests

* 15/02/26 [Arch] Plan-before-execute: validate all directives and sources before building the plan tree

* 15/02/26 [Feat] PlanNode DAG as immutable plan representation with per-node error isolation

* 15/02/26 [Task] Implement file cache with LRU eviction, path access control, and tests

* 15/02/26 [Arch] Lazy validation in file cache — skip filesystem checks for already-cached files

* 15/02/26 [Task] Implement directive parser with YAML block extraction and fragment decomposition

* 15/02/26 [Arch] Three-layer parsing pipeline: block detection, YAML parsing, fragment decomposition

* 15/02/26 [Feat] EmbedmContext as dependency injection container for config, file cache, and plugin registry

* 15/02/26 [Feat] Status-based error reporting with OK, WARNING, ERROR, FATAL levels