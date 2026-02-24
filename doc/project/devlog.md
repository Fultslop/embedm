# Dev Log

This document contains entries related to the work done or decisions on feature, architecture, implementation or code / design philosophy.

## Entries

* 24/02/26 [MISS] fix root directive skipping validate_input — `plan_file` and `plan_content` called `create_plan` directly, bypassing `plugin.validate_input` on the root node. Only child directives (processed via `_build_child`) ever reached `validate_input`, forcing plugin authors to handle root vs child as two separate cases. Fix: extracted `_validate_and_plan` helper from `_build_child` containing the validate→plan→artifact sequence; `plan_file`, `plan_content`, and `_build_child` all now delegate to it.

* 23/02/26 [ARCH] feat_verify_cli_option — three design decisions added: (1) compilation errors exit 1 in all modes (not just verify), correcting prior soft-fail behaviour; (2) line_endings config option (lf|crlf, default lf) applied before write and before verify comparison — project-level not directive-level; (3) verify-mode summary reports files_checked/up-to-date/stale instead of files_written.

* 23/02/26 [TASK] bug_clean_text_mangles_snake_case — fix: add word-boundary guards (?<!\w) / (?!\w) to the _{1,3}(.*?)_{1,3} italic-removal regex in text_processing._clean_text; regression tests in text_processing_test.py.

* 23/02/26 [ARCH] split CLAUDE.md — extracted full coding guidelines to doc/project/guidelines.md; CLAUDE.md slimmed to hard constraints + platform + session-start pointer (~20 lines). agent_context.src.md updated to embed guidelines.md instead of CLAUDE.md, eliminating the circular reference. Archiving policy note moved to guidelines.md.

* 23/02/26 [SUGGESTION] bug: _clean_text underscore italic regex mangles snake_case identifiers in recall output (e.g. plugin_resources.py → pluginresources.py). The _{1,3}(.*?)_{1,3} pattern matches across word boundaries when multiple underscores appear on one line. Recall output is semantically correct but identifiers are less readable. Fix: anchor underscore matching to word boundaries or exclude underscores surrounded by word characters.

* 23/02/26 [TASK] feat_agent_context_document — initial implementation: doc/project/agent_context.src.md with recall/file directives (CLAUDE.md whole + devlog recall for plugin conventions / architectural rules / miss patterns + active spec file embed); doc/project/embedm-config.yaml; compiled to doc/project/agent_context.md. CLAUDE.md updated with session-start instruction, recompile command, xenon threshold, devlog archiving policy. Dropped quality-thresholds recall section (xenon already in CLAUDE.md).

* 23/02/26 [TASK] recall_plugin.md — added "Building an AI agent context document" section with step-by-step instructions: identify sources, write directives, compile, point agent to output, recompile on change, track misses, run promotion gate before archiving. Updated feat_agent_context_document.md spec: archiving is user-executed, embedm assists preparation only via recall; execution is manual cut/paste to devlog_archive.md.

* 23/02/26 [ARCH] devlog archiving policy — [TASK]/[FEAT] entries may be archived; [ARCH]/[STANDARDS]/[MISS]/[REVIEW] are permanent and never archived. Before archiving, recall over the batch with "convention rule architectural decision" to surface untagged decisions for promotion to CLAUDE.md. Archive kept as devlog_archive.md for deep-history recall. Captured in feat_agent_context_document.md.

* 23/02/26 [FEAT] feat_agent_context_document — spec added to backlog/open/features/v1.0. Compiled context document using recall/file/query-path directives to pre-filter project knowledge for agent at session start. Four sections: plugin conventions, embed patterns, architectural decisions, active work. Effectiveness measured via [MISS] frequency in devlog.

* 23/02/26 [MISS] hardcoded version string in recall_plugin.md instead of using query-path directive. Correct pattern was established in doc/manual/src/readme.md. Root cause: read table_plugin.md and synopsis_plugin.md (neither has a version line) but did not read readme.md despite user citing it. Rule added to CLAUDE.md: read an existing compiled document in the same directory before writing any embed directive.

* 23/02/26 [TASK] recall_plugin manual — write doc/manual/src/recall_plugin.md covering use case, offline-RAG selling point, yaml embed examples, TOC, version, recall-vs-synopsis comparison.

* 23/02/26 [TASK] extract text_processing module — moved shared NLP pipeline (_clean_text, _split_into_blocks, _block_to_sentences, _tokenize, _score_frequency, _select_top, _build_word_freq, _sentence_score) from synopsis_transformer into embedm_plugins.text_processing; synopsis_transformer and recall_transformer now both import from the shared module.

* 23/02/26 [TASK] feat_recall_plugin — new recall plugin: query-based sentence retrieval using sparse token-overlap scoring; shares _clean_text / _split_into_blocks / _tokenize / _score_frequency / _select_top pipeline from synopsis_transformer; falls back to frequency scoring with a note when no sentences match the query. Registered as entry point and added to DEFAULT_PLUGIN_SEQUENCE after synopsis.

* 22/02/26 [TASK] feat_dry_run_cli_option — wire --dry-run / -n flag in cli.py; is_dry_run already existed on Configuration and orchestration already respected it. 3 new tests; 565 pass.

* 22/02/26 [REVIEW] feat_dry_run_cli_option — original spec said "only runs the planner, does not compile" but orchestration code already compiles fully and redirects to stdout. CLI flag also not yet wired up in cli.py. Spec updated to reflect actual intent: compile + print to stdout, no file write. is_dry_run field and orchestration logic already exist; only cli.py wiring remains.

* 22/02/26 [REVIEW] feat_verify_cli_option — original draft conflated two features: (1) CI staleness gate (`--verify`) and (2) incremental compilation with manifest. Settled on compile-compare-no-write approach: full compile runs, result compared byte-for-byte against existing output file, exit 1 if stale or missing. Timestamp/manifest approach rejected (unreliable in CI). Incremental compilation deferred to v2.0. Spec updated with AC1-AC8.

* 22/02/26 [TASK] feat_add_time_to_verbose — add per-node timing to verbose output: FileCache.on_event callback gains elapsed_s float; cache misses log "[cache miss] X.XXXs — path"; validate_directive and validate_input timed in planner; transform timed in orchestration; RunSummary.elapsed_s always appended to summary line as "completed in X.XXXs". New verbose_timing() helper in console.py. 6 new tests.

* 22/02/26 [TASK] feat_plugin_configurability — implement plugin_configuration section in embedm-config.yaml: Configuration.plugin_configuration field; config_loader parses and validates inner dicts; PluginBase gets get_plugin_config_schema() and validate_plugin_config() with no-op defaults; PluginConfiguration carries plugin_settings; orchestration._validate_plugin_configs() runs two-phase validation (schema type-check + plugin semantic); extraction.py gains DEFAULT_REGION_START/END constants and _compile_region_pattern() factory; RegionParams accepts template overrides; FilePlugin publishes schema and validates {tag} presence; region templates threaded end-to-end. 14 new tests; 557 pass.

* 22/02/26 [ARCH] feat_plugin_configurability — settled design: `plugin_configuration` section in `embedm-config.yaml` (no separate file); two-phase validation: framework validates structure via `get_plugin_config_schema()`, plugin validates semantics via `validate_plugin_config()`; unknown keys silently ignored (logged with --verbose); missing keys fall back to hardcoded defaults. Captured in spec acceptance criteria and features.md design decisions.

* 22/02/26 [TASK] Refactor embedm_plugins — split monolithic plugin_resources.py into five per-plugin resource files (file_resources, query_path_resources, synopsis_resources, table_resources, toc_resources); renamed normalize_json/yaml/xml/toml to query_path_normalize_* to make ownership explicit. Updated all source and test imports. Widened manual regression test allowed_paths to include project root so cross-directory references (e.g. pyproject.toml) resolve correctly.

* 22/02/26 [Fix] query-path trailing newline — scalar and format-string output from QueryPathTransformer now always appends \n so the blank-line separator after a directive fence is preserved in the rendered document.

* 22/02/26 [TASK] feat_add_toml_to_query_path — add TOML source support to query-path plugin via stdlib tomllib; new normalize_toml module; wired into _parse/_parse_error_message/_SUPPORTED_EXTENSIONS/_EXT_TO_LANG_TAG.

* 22/02/26 [TASK] feat_add_format_option_to_query_path — add optional `format: "{value}"` option to query-path directive; validates placeholder presence, path requirement, and scalar constraint; wired through artifact → transformer params → execute.

* 22/02/26 [TASK] feat_add_toml_to_query_path, feat_add_format_option_to_query_path — captured backlog specs for TOML source support and a `format: "{value}"` option on the query-path directive.

* 22/02/26 [TASK] feat_verbose_cli_option — update spec (stderr, all config fields, two-stage plugin discovery, planning tree node definition, lookup failure shows available types, NO_COLOR convention noted), then implement -v/--verbose flag.

* 22/02/26 [TASK] feat_query_path_plugin — implement QueryPathPlugin: normalize_json/yaml/xml normalizers, shared dot-notation query engine with backtick literal-key escaping, shared presenter (scalar → inline, dict/list → fenced yaml block, full-doc → fenced source block). Plugin registered after file in plugin_sequence. Tests: unit per module + regression example.

* 22/02/26 [REVIEW] feat_json_plugin generalization — reviewed FS proposal to extend JSON/YAML plugin to a unified query pipeline (normalize → query → present) covering JSON, YAML, XML, and directory structures with glob-style path queries.

* 22/02/26 [SUGGESTION] feat_json_plugin generalization — scope the query pipeline to data files only (JSON, YAML, XML) in v1; split directory/file-tree embedding into a separate backlog item. Glob-path queries also deferred: single dot-notation paths cover the primary use case without a result-aggregation model. See feat_json_plugin.md comments.

* 22/02/26 [TASK] Moved feat_recall_plugin to ready_for_implementation (not yet in active sprint). Created ready_for_implementation/ directory.

* 22/02/26 [SUGGESTION] feat_stats_loc (v2.0): LoC metric deferred from stats plugin — language detection reuses symbol extraction infrastructure; not worth bloating v1.0 stats plugin for a code-specific use case.

* 21/02/26 [FEAT] feat_synopsis_plugin — block model: split text on blank lines into blocks, apply positional decay weight 1/(1+block_idx) to sentence scores, add `sections` option (0=all) to cap input to first N blocks. Renamed _split_sentences → _block_to_sentences, added _split_into_blocks. Quality: table_plugin and moby_dick outputs dramatically improved; man_ls improved but nroff header (block 0) still contaminates due to block 0 weight advantage.

* 21/02/26 [TASK] feat_synopsis_plugin — implement synopsis plugin: stopword-based sentence scoring (Frequency + Luhn algorithms), EN/NL language support, blockquote output, reads parent_document string fragments (post-embed pass), runs before toc in plugin_sequence.

* 21/02/26 [REVIEW] feat_synopsis_plugin — synopsis runs as a DFS pass between file and toc in plugin_sequence. Text extraction from parent_document string fragments naturally skips Directive objects (embedm blocks already parsed). Fenced code blocks and table rows stripped before scoring. Determinism guaranteed by tie-breaking on original sentence index. Source option: use file_cache.get_file() when directive.source is set, no planner changes needed.

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