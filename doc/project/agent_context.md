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

> 23/02/26 [TASK] featagentcontextdocument — initial implementation: doc/project/agentcontext.src.md with recall/file directives (CLAUDE.md whole + devlog recall for plugin conventions / architectural rules / miss patterns + active spec file embed); doc/project/embedm-config.yaml; compiled to doc/project/agent_context.md. Registered as entry point and added to DEFAULTPLUGIN_SEQUENCE after synopsis. 22/02/26 [TASK] Refactor embedmplugins — split monolithic pluginresources.py into five per-plugin resource files (fileresources, querypathresources, synopsisresources, tableresources, tocresources); renamed normalizejson/yaml/xml/toml to querypathnormalize to make ownership explicit. 22/02/26 [TASK] featverboseclioption — update spec (stderr, all config fields, two-stage plugin discovery, planning tree node definition, lookup failure shows available types, NOCOLOR convention noted), then implement -v/--verbose flag. 19/02/26 [Arch] Plugin load failures treated as user errors — `loadplugins` now returns `list[Status]` and catches per-entry exceptions gracefully.

## Architectural rules

Core rules about the validation/transform boundary, error handling, and code quality.

> 23/02/26 [ARCH] split CLAUDE.md — extracted full coding guidelines to doc/project/guidelines.md; CLAUDE.md slimmed to hard constraints + platform + session-start pointer (~20 lines). 22/02/26 [TASK] featpluginconfigurability — implement pluginconfiguration section in embedm-config.yaml: Configuration.pluginconfiguration field; configloader parses and validates inner dicts; PluginBase gets getpluginconfigschema() and validatepluginconfig() with no-op defaults; PluginConfiguration carries pluginsettings; orchestration.validatepluginconfigs() runs two-phase validation (schema type-check + plugin semantic); extraction.py gains DEFAULTREGIONSTART/END constants and compileregion_pattern() factory; RegionParams accepts template overrides; FilePlugin publishes schema and validates {tag} presence; region templates threaded end-to-end. 22/02/26 [ARCH] featpluginconfigurability — settled design: `pluginconfiguration` section in `embedm-config.yaml` (no separate file); two-phase validation: framework validates structure via `getpluginconfigschema()`, plugin validates semantics via `validatepluginconfig()`; unknown keys silently ignored (logged with --verbose); missing keys fall back to hardcoded defaults. 21/02/26 [REVIEW] techmovevalidationfromtabletransformerexecute — pipeline steps (applyselect, applyorderby) currently return errors via CAUTION strings; for the transformer to be fully pure, column/expression validation must also move to validateinput. 16/02/26 [Standards] Error handling guidelines — coding errors crash via assert, input errors collect Status and recover.

## Patterns — avoid these misses

Established patterns that have caused errors when overlooked. Check these before writing any embed directive or adding a plugin.

> agent_context.src.md updated to embed guidelines.md instead of CLAUDE.md, eliminating the circular reference. Compiled context document using recall/file/query-path directives to pre-filter project knowledge for agent at session start. 23/02/26 [MISS] hardcoded version string in recallplugin.md instead of using query-path directive. Correct pattern was established in doc/manual/src/readme.md.

## Active feature spec

FEATURE: Agent Context Document
========================================
Draft  
Release v1.0  
Created: 23/02/2026  
Closed: 23/02/2026  
Created by: FS / Claude  

## Description

Create a compiled markdown document that pre-filters project knowledge for the AI agent
at session start. The agent reads this document instead of manually scanning CLAUDE.md,
devlog.md, and active specs separately.

Each Claude session starts cold with no memory of previous decisions. CLAUDE.md provides
rules but not history. The devlog provides history but requires scanning. The context
document bridges the gap: it uses recall and file directives to compile pre-targeted
queries into a single, focused reference that surfaces what the agent needs without
loading everything.

This is dog-fooding: embedm is used to build the context that improves embedm's own
development. The quality of the context document can be tracked via `[MISS]` entries
in the devlog (errors the document should have prevented).

Related: the document's long-term usefulness depends on devlog knowledge not being lost
to archiving. A companion devlog archiving policy (see Design notes) is part of this feature.

### Design notes

**Source and output locations**

- Source: `doc/project/src/agent_context.md`
- Compiled output: `doc/project/agent_context.md`
- The source uses recall, file, and query-path directives against project files.

**Sections**

The compiled document has four sections drawing from different sources:

1. **Plugin conventions** — recall over devlog and source files: registration patterns,
   resource file naming, entry point format, DEFAULT_PLUGIN_SEQUENCE placement.
2. **Embed patterns** — recall over `doc/manual/src/readme.md` and compiled manual docs:
   how project metadata (version, name) is embedded dynamically, established directive idioms.
3. **Architectural decisions** — recall over devlog (permanent tags only): validation/transform
   boundary, xenon thresholds, transformer purity rule, text_processing shared module.
4. **Active work** — file embed of the current in-progress spec from
   `doc/project/backlog/in_progress/`. Not recall — the full spec is needed.

**Devlog archiving policy**

The context document draws from the live devlog. As the devlog grows, recall results
become noisier. The archiving policy ensures knowledge is preserved without polluting
current queries.

*Tag retention rules (enforced by convention, never automated):*

- `[TASK]` and `[FEAT]` entries may be archived once they are sufficiently old.
- `[ARCH]`, `[STANDARDS]`, `[MISS]`, and `[REVIEW]` entries are **never archived** —
  they stay in the live devlog permanently.

*Archiving process (user-executed, embedm-assisted):*

embedm cannot move entries between files — it is a compiler, not an editor. Archiving
is a manual operation performed by the user. embedm assists only the preparation step.

1. When the devlog becomes large enough to affect recall quality, the user creates a
   temporary source document with a recall directive over the entries to be archived:
   ```yaml
   type: recall
   source: ./devlog.md
   query: "convention rule architectural decision established"
   max_sentences: 8
   ```
2. Compile and review the output (the promotion gate). Any surfaced decision not already
   in CLAUDE.md must be promoted before proceeding.
3. The user manually moves old `[TASK]` and `[FEAT]` entries from `devlog.md` to
   `devlog_archive.md`.
4. The archive file is retained. The context document may include an optional recall
   over it for deep history.

**Measuring effectiveness**

`[MISS]` entries in the devlog record errors the context document should have prevented.
Compare the `[MISS]` frequency across sessions before and after the document is introduced.
This is the primary feedback signal for tuning the recall queries.

## Acceptance criteria

1. `doc/project/src/agent_context.md` exists as a source document using recall, file,
   and query-path directives targeting devlog.md, CLAUDE.md, and the active spec.
2. The source compiles cleanly with no errors or warnings.
3. The compiled output contains the four sections described above: plugin conventions,
   embed patterns, architectural decisions, active work.
4. CLAUDE.md is updated to reference the compiled document and instruct the agent to
   read it at session start before beginning any task.
5. The devlog archiving policy (permanent tags, user-executed archiving, embedm-assisted
   promotion gate) is documented in CLAUDE.md.
6. At least one recall query per section is tuned so that the relevant content (e.g.
   the resource file naming convention, the validation/transform boundary rule) appears
   in the compiled output.
7. After a simulated archive of old `[TASK]` entries, the compiled output of the context
   document is unaffected: decisions and patterns remain accessible.

## Comments

23/02/26 Claude: Discussed in doc/project/claude-dialogs/on_recall_dog_food.md.
  Core insight: devlog conflates audit trail (ephemeral) and decisions (permanent).
  Archiving must not conflate them. Tag-based retention prevents knowledge loss by
  construction; recall-based promotion gate catches untagged decisions before they
  are archived.
