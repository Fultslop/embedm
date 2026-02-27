TECHNICAL IMPROVEMENT: Unify directive planning into a single pathway
========================================
Draft  
Created: 25/02/26  
Created by: FS  

## Description

The planner currently has two separate code paths for building child `PlanNode` entries during `create_plan`:

- **Source directives** → `_build_children` → `_build_child` → `_validate_and_plan` → `create_plan` (recursive)
- **Source-less directives** → `_validate_sourceless_directives` → leaf `PlanNode`

Both paths need to call `normalize_input` and produce a `PlanNode` with an artifact. Having two parallel functions means any future change to the validate/plan/artifact logic must be applied in both places. The `_validate_sourceless_directives` function was introduced as a targeted fix rather than a structural one.

The correct approach is a single `_plan_directive` function that:

1. Calls `plugin.normalize_input` (with file content for source directives, `""` for source-less)
2. On validation errors: returns an error node
3. If source present: recurse via `create_plan`, set artifact, return node
4. If source-less: return leaf node with artifact

This replaces `_validate_sourceless_directives`, `_build_child`, and `_validate_and_plan` with a single unified function. `_build_children` becomes a simple list comprehension over it.

## Acceptance criteria

- `_validate_sourceless_directives`, `_build_child`, and `_validate_and_plan` are removed
- A single `_plan_directive(directive, depth, ancestors, context, plugin_config) -> PlanNode` handles all directive types
- All existing planner tests pass without modification
- New tests for the unified path cover: source directive with artifact, source-less directive with artifact, errors in both cases

## Comments

25/02/26 FS: The current two-path fix is acceptable as a stopgap. This refactor is the proper long-term solution.
