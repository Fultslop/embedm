# Dev Log

This document contains entries related to the work done or decisions on feature, architecture, implementation or code / design philosophy.

## Entries

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