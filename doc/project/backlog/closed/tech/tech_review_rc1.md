TECHNICAL IMPROVEMENT: Code Review RC 1
========================================
Draft
Created: 23/02/2026
Closed: `<date>`
Created by: FS

## Description

Review base (./src). Look specifically where we can ensure single responsibility. Right now files like orchestration.py and to a lesser extend planner.py start to feel bloated and do more than they should. Maybe we should break them up. 

Look for inconsistent use of design patterns and come up for improvements. 

Look for violations against the scope of the project as expressed in `doc\project\features.md`

We want a easy-to-understand, easy-to-modify, sound and mature code base that you Claude would be proud of! 

## Acceptance criteria

* An inventory of actionable items within the scope of refactoring added to the comment section below.

## Comments

23/02/26 Claude: Inventory of actionable refactoring items

---

**R1 — orchestration.py: verify logic should live in its own module**
- File: `orchestration.py`
- Issue: `_VerifyStatus`, `_verify_file_output`, and `_apply_line_endings` are verify-mode concerns bundled into a general orchestration module.
- Suggestion: Extract to a new `verification.py` module in the application layer.

**R2 — orchestration.py: three independent tree-walk functions**
- File: `orchestration.py`
- Issue: `_collect_tree_errors`, `_tree_has_level`, and `_collect_embedded_sources` all recursively traverse PlanNode trees with ad-hoc accumulators; no shared traversal abstraction.
- Suggestion: Move to a `plan_tree.py` utility (domain or application layer) and unify the traversal loop.

**R3 — orchestration.py: `_resolve_config` manually mirrors every Configuration field**
- File: `orchestration.py`, `configuration.py`
- Issue: Every new config field requires two edits — the dataclass and the explicit merge in `_resolve_config`.
- Suggestion: Add a `Configuration.merge(cli_config, file_config)` class method that uses `dataclasses.replace` or similar, making the merge self-maintaining.

**R4 — plugin_registry.py: `find_plugin_by_directive_type` is O(n)**
- File: `plugin_registry.py`
- Issue: The `lookup` dict is keyed by plugin *name*; every directive lookup linearly scans all plugins to match on `directive_type`.
- Suggestion: Maintain a secondary `_by_directive_type: dict[str, PluginBase]` populated in `load_plugins()` for O(1) lookup.

**R5 — planner.py: `_validate_directives` does three things and returns a raw 3-tuple**
- File: `planner.py`
- Issue: The function checks plugin existence, validates directives, and validates sources, returning `(errors, buildable, error_children)` — a stringly-typed contract.
- Suggestion: Split into `_check_plugins` and `_check_sources`, or introduce a small result dataclass to make the contract explicit.

**R6 — directive.py: option casting/validation methods on a domain dataclass**
- File: `domain/directive.py`
- Issue: `validate_option()` and `get_option()` perform type casting and validation inside a plain data container; this is application/plugin logic, not domain state.
- Suggestion: Move these helpers to `PluginBase` or a `DirectiveOptions` utility so the domain object stays pure.

**R7 — config_loader.py / orchestration.py: similar names for different validation jobs**
- Files: `config_loader.py`, `orchestration.py`
- Issue: `_validate_plugin_configuration` (validates YAML structure at load time) and `_validate_plugin_configs` (validates against live plugin schemas at startup) have nearly identical names despite serving different phases.
- Suggestion: Rename to `_validate_plugin_config_structure` and `_validate_plugin_config_schemas` respectively to make the distinction obvious.

