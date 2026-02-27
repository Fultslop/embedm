TECHNICAL IMPROVEMENT: Event system
=============================================================================
Created: 27/02/2026
Closed: 27/02/2026
Created by: Claude

## Description

Multiple internal systems produce output — the orchestrator, planner, compiler, plugin registry, and file cache. Currently they all call `console.py` display functions directly. This tight coupling makes it impossible to compose different output backends, test output in isolation, or extend to a multithreaded model.

This feature introduces a central event system. Every system that produces output emits typed events. Subscribers (renderers, log writers, test harnesses) receive those events and decide how to handle them. The orchestration layer is decoupled from all display concerns.

### Design principles

- **Typed events** — each event is a Python dataclass with explicit fields. No untyped dicts or string payloads.
- **Consumer-side filtering** — producers always emit; subscribers decide what to act on based on verbosity or other criteria.
- **Synchronous dispatch** — events are delivered to subscribers immediately on the emitting thread. See the multithreading note for the planned evolution.
- **Single dispatcher** — one `EventDispatcher` instance lives in `EmbedmContext`, making it accessible to any system that holds a context reference.

### Dispatcher

The dispatcher is a minimal publish/subscribe mechanism.

```
EventDispatcher:
  subscribe(event_type: type[EmbedmEvent], listener: Callable[[EmbedmEvent], None]) -> None
  emit(event: EmbedmEvent) -> None
```

- A subscriber registers for a specific event type. Subclasses do not automatically match a parent type subscription.
- Multiple subscribers for the same type are notified in registration order.
- `emit()` calls all matching subscribers synchronously before returning.
- The dispatcher does not filter by verbosity — that is the subscriber's responsibility.

### Event catalog

All events inherit from `EmbedmEvent`. Fields marked with `*` are relative paths.

**Session lifecycle**

| Event | Fields |
|---|---|
| `SessionStarted` | `version: str`, `config_source: str`, `input_type: str`, `output_type: str` |
| `SessionComplete` | `ok_count: int`, `error_count: int`, `total_elapsed: float` |

`config_source` is `"DEFAULT"` when no config file is used, otherwise the relative path to the config file.
`input_type` / `output_type` are one of `"stdin"`, `"stdout"`, `"file"`, `"directory"`.

**Plugin loading**

| Event | Fields |
|---|---|
| `PluginsLoaded` | `discovered: int`, `loaded: int`, `errors: list[str]` |

**Planning**

| Event | Fields |
|---|---|
| `PlanningStarted` | `file_count: int` |
| `FilePlanned` | `file_path*: str`, `index: int`, `total: int` |
| `FilePlanError` | `file_path*: str`, `index: int`, `total: int`, `message: str` |
| `PlanningComplete` | `file_count: int`, `error_count: int` |

`index` is 1-based throughout.

**Compilation**

| Event | Fields |
|---|---|
| `CompilationStarted` | `file_count: int` |
| `FileStarted` | `file_path*: str`, `node_count: int`, `index: int`, `total: int` |
| `NodeCompiled` | `file_path*: str`, `node_index: int`, `node_count: int`, `elapsed: float` |
| `FileCompleted` | `file_path*: str`, `output_path*: str`, `elapsed: float`, `index: int`, `total: int` |
| `FileError` | `file_path*: str`, `message: str`, `elapsed: float`, `index: int`, `total: int` |
| `CompilationComplete` | `ok_count: int`, `error_count: int` |

`elapsed` in compilation events is the time in seconds since `FileStarted` was emitted for that file.
`message` in `FileError` is the exception message only — not the full traceback.

**Infrastructure**

| Event | Fields |
|---|---|
| `CacheEvent` | `kind: str`, `key: str`, `elapsed: float` |

`kind` is one of `"hit"`, `"miss"`, `"eviction"`. `elapsed` is `0.0` for eviction events.

This replaces the existing `on_event: Callable[[str, str, float], None]` callback in `FileCache`. `FileCache` receives the `EventDispatcher` and emits `CacheEvent` directly.

**Plugin diagnostics**

| Event | Fields |
|---|---|
| `PluginDiagnostic` | `plugin_name: str`, `file_path*: str`, `level: StatusLevel`, `message: str` |

`level` uses the existing `StatusLevel` domain type (`WARNING`, `ERROR`). `FATAL` is not appropriate here — a fatal plugin condition should raise an exception instead.

Plugins emit this event via `PluginContext`. `PluginContext` exposes `emit_diagnostic(level, message)` which constructs and emits `PluginDiagnostic` with the plugin name and current file path pre-filled from context.

### Producer integration

| Producer | Integration point | Emits |
|---|---|---|
| Orchestrator | Calls `context.events.emit(...)` | Session, plugin, planning, compilation events |
| Planner | Receives `EventDispatcher`, emits during planning | `FilePlanned`, `FilePlanError` |
| Compiler | Receives `EventDispatcher`, emits during compilation | `FileStarted`, `NodeCompiled`, `FileCompleted`, `FileError` |
| Plugin registry | Receives `EventDispatcher`, emits after load | `PluginsLoaded` |
| File cache | Receives `EventDispatcher`, replaces `on_event` callback | `CacheEvent` |
| Plugins | Via `PluginContext.emit_diagnostic()` | `PluginDiagnostic` |

`EventDispatcher` is stored as `EmbedmContext.events`. All systems that already receive `EmbedmContext` or `PluginContext` gain access without signature changes.

### Consumer interface

Subscribers are plain callables: `Callable[[EmbedmEvent], None]`. A subscriber class implementing multiple handlers registers each handler separately for its specific event type.

Verbosity-aware subscribers receive all events and check the config verbosity (available through the context they hold) to decide whether to act.

### Relationship to other specs

- `tech_improve_output.md` — defines what the renderer subscriber shows for each event at each verbosity level. That spec is the display contract; this spec is the transport.
- `tech_output_renderer.md` — migrates `console.py` direct-print calls to event emissions and implements `InteractiveRenderer` / `StreamRenderer` as subscribers.
- `tech_batch_execution.md` — will extend the event catalog with `BatchStarted` and `BatchComplete` events when implemented.

### Future: multithreading

The current `emit()` is synchronous. When multithreaded file processing is introduced:

1. `emit()` puts events onto a thread-safe queue instead of calling listeners directly.
2. A dedicated renderer thread drains the queue and calls listeners.
3. Listeners do not change — they remain single-threaded from their own perspective.

This transition is an internal change to `EventDispatcher` only. No producer or subscriber code changes.

## Acceptance criteria

`<Optional: list of line description of tests to measure improvements>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
