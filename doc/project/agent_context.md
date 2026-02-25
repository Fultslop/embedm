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

> Updated `test_create_plan_directive_without_source` to reflect the new correct behaviour (source-less directives with a registered plugin now produce a child node). 24/02/26 [MISS] fix root directive skipping validate_input — `plan_file` and `plan_content` called `create_plan` directly, bypassing `plugin.validate_input` on the root node. Only child directives (processed via `_build_child`) ever reached `validate_input`, forcing plugin authors to handle root vs child as two separate cases. Fix: extracted `_validate_and_plan` helper from `_build_child` containing the validate→plan→artifact sequence; `plan_file`, `plan_content`, and `_build_child` all now delegate to it. Registered as entry point and added to DEFAULT_PLUGIN_SEQUENCE after synopsis.

## Architectural rules

Core rules about the validation/transform boundary, error handling, and code quality.

> 23/02/26 [ARCH] feat_verify_cli_option — three design decisions added: (1) compilation errors exit 1 in all modes (not just verify), correcting prior soft-fail behaviour; (2) line_endings config option (lf|crlf, default lf) applied before write and before verify comparison — project-level not directive-level; (3) verify-mode summary reports files_checked/up-to-date/stale instead of files_written. 23/02/26 [TASK] bug_clean_text_mangles_snake_case — fix: add word-boundary guards (?<!\w) / (?!\w) to the {1,3}(.?){1,3} italic-removal regex in text_processing._clean_text; regression tests in text_processing_test.py. 23/02/26 [ARCH] split CLAUDE.md — extracted full coding guidelines to doc/project/guidelines.md; CLAUDE.md slimmed to hard constraints + platform + session-start pointer (~20 lines). 21/02/26 [REVIEW] tech_move_validation_from_table_transformer_execute — pipeline steps (_apply_select, _apply_order_by) currently return errors via CAUTION strings; for the transformer to be fully pure, column/expression validation must also move to validate_input. 16/02/26 [Standards] Error handling guidelines — coding errors crash via assert, input errors collect Status and recover.

## Patterns — avoid these misses

Established patterns that have caused errors when overlooked. Check these before writing any embed directive or adding a plugin.

> Added `_rel(path)` helper (CWD-relative POSIX string, fallback to original) to `file_cache.py` and `planner.py`; applied to all path-bearing error strings in `validate()`, `write()`, `get_files()` (file_cache) and `plan_file()`, `_validate_source()`, `_build_child()` (planner). 25/02/26 [ARCH] tech_unify_directive_planning — the current fix for source-less directives (`_validate_sourceless_directives`) is a parallel code path rather than a unified one. Compiled context document using recall/file/query-path directives to pre-filter project knowledge for agent at session start. 23/02/26 [MISS] hardcoded version string in recall_plugin.md instead of using query-path directive.

## Active feature spec

implement `doc_document_query_path_plugin.md` in `doc\project\backlog`.

If you can't find this because the active spec may be moved or renamed, ask the user.