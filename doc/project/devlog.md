# Dev Log

This document contains entries related to the work done or decisions on feature, architecture, implementation or code / design philosophy.

## Entries

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