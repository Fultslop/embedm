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
