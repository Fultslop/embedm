TECHNICAL IMPROVEMENT: Output renderer
=============================================================================
Draft
Created: 27/02/2026
Closed: `<date>`
Created by: Claude

## Description

`console.py` currently contains 20+ display functions called directly from `orchestration.py`, `compiler.py`, and other modules. This tight coupling prevents the event-driven output model described in `tech_improve_output.md` and `tech_event_system.md`.

This feature migrates the output system from direct `console.py` calls to renderer subscribers on the event dispatcher. It is a refactoring ticket: **no user-visible behavior changes**. The output continues to look and behave as it does today; this just restructures how that output is produced.

This ticket is a prerequisite for implementing the UX changes in `tech_improve_output.md`.

### Scope

1. **Introduce the `EventDispatcher`** (defined in `tech_event_system.md`) into `EmbedmContext`.

2. **Migrate producers** — replace direct `console.py` calls in `orchestration.py`, `compiler.py`, `planner.py`, and `plugin_registry.py` with `context.events.emit(...)`. Replace the `FileCache.on_event` callback with `EventDispatcher`.

3. **Introduce the renderer interface** — a protocol / abstract base that renderers implement:
   ```
   Renderer:
     subscribe(dispatcher: EventDispatcher) -> None
   ```
   `subscribe()` registers the renderer's handlers for all event types it cares about.

4. **Implement `LegacyRenderer`** — a renderer that subscribes to all events and reproduces the current `console.py` output exactly. This is a direct port of the existing display logic, not a redesign. After this step, behavior is unchanged and `console.py` is no longer called from orchestration.

5. **Delete or reduce `console.py`** — once all call sites are migrated, `console.py` is either deleted or reduced to helpers used only by `LegacyRenderer`.

### Out of scope

- The interactive live-progress display (`InteractiveRenderer`) — implemented in `tech_improve_output.md`.
- The stream renderer for non-TTY output — implemented in `tech_improve_output.md`.
- Any change to what is shown or how it is formatted — that belongs to `tech_improve_output.md`.
- Color — belongs to `tech_improve_output.md`.

### Implementation order

1. Add `EventDispatcher` to `EmbedmContext`.
2. Implement `LegacyRenderer` that calls the existing `console.py` functions.
3. Migrate one producer at a time, verifying existing tests pass after each.
4. Remove `console.py` once all producers are migrated and all call sites are gone.

## Acceptance criteria

- All existing tests pass without modification.
- `console.py` is deleted or contains only internal helpers with no call sites in orchestration.
- No direct `print()` calls remain in `orchestration.py`, `compiler.py`, or `planner.py`.

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
