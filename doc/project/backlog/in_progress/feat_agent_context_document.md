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
