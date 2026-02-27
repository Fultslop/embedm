# Agent Context

This document is compiled from project sources to give Claude focused context at session start.
Read this before beginning any task. It does not replace the files it draws from — go to the source
for full detail.

## Project guidelines

# Development Guidelines

## Plugin Architecture

The plugin pipeline is: `Plugin → Validate → Transform`

**Transformers are pure.** A transformer receives validated input and returns a string. It never validates input or returns errors — that belongs in the Validate step. If you find validation logic inside a transformer, it is a bug.

---

## Documentation

Log every task in `./doc/project/devlog.md` **before starting work**. Most recent entry first.

Format: `DD/MM/YY [TAG] Description`

Tags: `REVIEW`, `SUGGESTION`, `TASK`, `ARCH`, `FEAT`, `STANDARDS`, `MISS`

Use `[MISS]` when documenting a correction: something that should have been known from existing project context but was not. Include what was missed and where the correct pattern was.

---

## Agent Execution

- Review the spec and related code before implementing. Flag issues, ambiguities, and suggest improvements.
- Specs are in `./doc/project/backlog/ready_for_implementation`.
- If scope is exceeded during implementation, defer to the user. Propose a backlog item using templates in `./doc/project/backlog/templates`.
- Document all suggestions in `devlog.md` with `[SUGGESTION]`.
- Run Radon/Xenon occasionally during implementation to check for complexity issues early.
- Before writing any embed directive in a compiled document (`doc/manual/src/`, etc.), read at least one existing compiled document in the same directory to identify established patterns. Never hardcode a value that could be embedded dynamically (version, project name, etc.).

---

## Coding Rules

- Type hints required for all code.
- Public APIs must have docstrings. Never include usage examples in docstrings.
- Line length: 120 chars maximum.
- Testing: `pytest`. Cover edge cases and errors. New features require tests; bug fixes require regression tests.
- Prefer low cyclomatic complexity.

---

## Code Style

- PEP 8: `snake_case` functions/variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.
- Use f-strings for formatting.
- Boolean names start with a verb: `is_valid`, `has_content`, `show_link`.
- Prefer `if condition` over `if not condition` unless it complicates the logic.
- Define composing functions before their components.
- Mark issues in existing code with `TODO:`.

---

## Coding Best Practices

- Minimize code footprint. Clean up dead code.
- DRY. Don't repeat yourself.
- Single responsibility for classes and functions.
- Prefer functional, immutable approaches when not verbose.
- Only modify code related to the task at hand.
- Keep core logic clean; push implementation details to the edges.
- Assert preconditions on all public methods.
- User-facing strings must be centralized (usually `module_resources.py`). Programming errors can have inline strings.

---

## Python Tools

- Format/lint: `ruff check ./src` — fix: `ruff check ./src --fix`
- Type check: `mypy ./src`
- Complexity: `xenon --max-absolute B --max-modules A --max-average A ./src`
- Fix order for CI failures: formatting → type errors → linting

---

## Devlog Archiving Policy

`[TASK]` and `[FEAT]` entries may be archived once sufficiently old.
`[ARCH]`, `[STANDARDS]`, `[MISS]`, and `[REVIEW]` entries are **never archived** — they stay
in the live devlog permanently.

Before archiving, run the promotion gate: create a temporary source document with a recall
directive over the devlog querying `"convention rule architectural decision established"`,
compile it, and promote any surfaced decisions not already in guidelines.md. Then manually move
old `[TASK]`/`[FEAT]` entries to `devlog_archive.md`.

## Plugin conventions

Key decisions about plugin structure, registration, and naming extracted from the decision log.

> `_build_context(config)` split into `_load_plugins(config) → (PluginRegistry, errors)` and `_build_context(config, registry) → EmbedmContext` for explicit plugin-load staging. 27/02/26 [TASK] feat_plugin_debugging — `-p`/`--plugin-list` CLI flag + `PluginDiagnostics` service + WARNING on unresolved `plugin_sequence` entries. New `PluginDiagnostics.check()` returns `WARNING` statuses for `plugin_sequence` modules with no matching entry point. `_REQUIRED_ATTRS` constant and post-instantiation attribute check added to `plugin_registry.py`; missing attrs → `StatusLevel.FATAL` error using entry-point name as identifier. Deduplication by module path added to `load_plugins` to prevent duplicate entry-point registrations from producing duplicate errors.

## Architectural rules

Core rules about the validation/transform boundary, error handling, and code quality.

> `_build_context(config)` split into `_load_plugins(config) → (PluginRegistry, errors)` and `_build_context(config, registry) → EmbedmContext` for explicit plugin-load staging. `_handle_plugin_load_errors` extracted from `main()` to handle fatal load errors (present + `sys.exit(1)`); `_exit_if_errors` and `_exit_on_run_failure` extracted to bring `main()` to cyclomatic complexity A (3). Deduplication by module path added to `load_plugins` to prevent duplicate entry-point registrations from producing duplicate errors. File plugin applies transformer post-extraction. 21/02/26 [REVIEW] tech_move_validation_from_table_transformer_execute — pipeline steps (_apply_select, _apply_order_by) currently return errors via CAUTION strings; for the transformer to be fully pure, column/expression validation must also move to validate_input.

## Patterns — avoid these misses

Established patterns that have caused errors when overlooked. Check these before writing any embed directive or adding a plugin.

> `_glob_base`, `_extract_base_dir`, `_expand_directory_input`, `apply_line_endings` moved to `infrastructure/file_util.py` (functions made public; `expand_directory_input` gains `pattern=".md"` default). Three hardcoded strings in `_validate_plugin_config_schemas` replaced with `app_resources` entries. Startup warning path added alongside normal compilation flow. 23/02/26 [MISS] hardcoded version string in recall_plugin.md instead of using query-path directive.

## Active feature spec

implement `doc_document_query_path_plugin.md` in `doc\project\backlog`.

If you can't find this because the active spec may be moved or renamed, ask the user.