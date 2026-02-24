# Architecture

version 0.9.6

embedm is a markdown document compiler. Source files containing ```` ```yaml embedm ```` directive blocks are read, a plan tree is built and validated, and then each directive is resolved by a plugin and replaced with its compiled output. The result is a complete, self-contained markdown document.

This document covers the core architecture for users who want to understand how the system works and for developers writing plugins.

  - [Domain Entities](#domain-entities)
    - [Directive](#directive)
    - [Document and Fragments](#document-and-fragments)
    - [PlanNode](#plannode)
    - [Status and StatusLevel](#status-and-statuslevel)
  - [Plugin Architecture](#plugin-architecture)
    - [PluginBase](#pluginbase)
    - [Plugin Discovery](#plugin-discovery)
    - [PluginRegistry](#pluginregistry)
  - [Plan / Compile Two-Phase Model](#plan-compile-two-phase-model)
    - [Phase 1: Plan](#phase-1-plan)
    - [Phase 2: Compile](#phase-2-compile)
  - [Error Model](#error-model)
    - [Status Levels](#status-levels)
    - [Error Propagation](#error-propagation)
    - [Compile-time Errors](#compile-time-errors)
  - [Document Model](#document-model)
    - [The Fragment Sequence](#the-fragment-sequence)
    - [Multi-pass Compilation](#multi-pass-compilation)
    - [Why plugin_sequence Order Matters](#why-plugin-sequence-order-matters)
  - [Orchestration Flow](#orchestration-flow)
  - [Infrastructure Services](#infrastructure-services)
    - [FileCache](#filecache)
    - [Directive Parser](#directive-parser)

## Domain Entities

The domain layer is a small set of immutable dataclasses that flow through the entire system. No business logic lives here; they are pure data carriers.

### Directive

A `Directive` represents a single parsed embedm block. It holds the `type` string that identifies which plugin handles it, an optional `source` path, a dict of additional `options`, and the `base_dir` of the file that contains it (used for relative link computation).

```python
@dataclass
class Directive:
    type: str
    source: str = ""
    options: dict[str, str] = field(default_factory=dict)
    base_dir: str = ""
```

### Document and Fragments

A `Document` wraps the parsed output of a single source file: its file name and an ordered list of `Fragment` objects.

```python
Fragment = str | Span | Directive

@dataclass
class Document:
    file_name: str
    fragments: list[Fragment] = field(default_factory=list)
```

A `Fragment` is one of three things:

- **`str`** — a literal text segment from the source file.
- **`Span`** — a `(offset, length)` reference into the original source bytes. Spans are resolved to strings during compilation.
- **`Directive`** — a parsed embedm block that will be replaced by its plugin's output during compilation.

The document is built once during planning and consumed during compilation.

### PlanNode

A `PlanNode` is one node in the plan tree. Every directive in a document becomes a child node of the document's root node. The tree is built recursively: if a directive's source is itself a markdown file containing directives, those are planned as grandchildren.

```python
@dataclass
class PlanNode:
    directive: Directive
    status: list[Status]
    document: Document | None
    children: list[PlanNode] | None
    artifact: Any                  # set by validate_input; available to transform()
```

`document` holds the parsed fragments of this node's source. It is `None` when planning failed before a document could be built. `artifact` carries structured data computed during the plan phase (e.g. a parsed JSON tree) so that the compile phase does not need to re-parse files.

### Status and StatusLevel

`Status` is the shared language for all error reporting: from directive parsing, through plugin validation, to compile-time failures.

```python
class StatusLevel(Enum):
    OK      = 1
    WARNING = 2
    ERROR   = 3
    FATAL   = 4

@dataclass
class Status:
    level: StatusLevel
    description: str
```

See [Error Model](#error-model) for how each level is handled by the orchestrator.

## Plugin Architecture

### PluginBase

Every plugin is a class that inherits from `PluginBase` and declares three class-level attributes. The `hello_world_plugin` in the standard distribution is the canonical minimal example: no source, no options, just a `validate_directive` that checks the type and a `transform` that returns a fixed string. It is useful as a starting point when writing a new plugin.

```python
class PluginBase(ABC):
    name: ClassVar[str]           # human-readable name
    api_version: ClassVar[int]    # must be 1
    directive_type: ClassVar[str] # the type string matched in embedm blocks
```

The abstract interface has two mandatory methods and two optional ones:

| Method | Required | Purpose |
|--------|----------|---------|
| `validate_directive(directive, config)` | Yes | Check options syntax; return `list[Status]` |
| `transform(plan_node, parent_document, ...)` | Yes | Produce the compiled string output |
| `validate_input(directive, content, config)` | No | Parse the source file; return a typed `ValidationResult` |
| `validate_plugin_config(settings)` | No | Validate per-plugin config from `embedm-config.yaml` |

### Plugin Discovery

Plugins are discovered at startup via Python's `importlib.metadata` entry-point mechanism. Any installed package can register plugins under the `embedm.plugins` group in its `pyproject.toml`:

```toml
[project.entry-points."embedm.plugins"]
file        = "embedm_plugins.file_plugin:FilePlugin"
query-path  = "embedm_plugins.query_path_plugin:QueryPathPlugin"
toc         = "embedm_plugins.toc_plugin:ToCPlugin"
```

This makes the plugin system open: third-party packages install alongside embedm and their plugins become available without any changes to the core codebase.

### PluginRegistry

The `PluginRegistry` loads and indexes plugins at startup.

```python
registry.load_plugins(enabled_modules=set(config.plugin_sequence))
```

Only modules listed in `plugin_sequence` are loaded. Plugins from installed packages that are not in the sequence are discovered but skipped. After loading, two lookups are available:

- `registry.lookup[name]` — by plugin name (string).
- `registry.find_plugin_by_directive_type(type)` — by directive type; used by the planner and compiler.

## Plan / Compile Two-Phase Model

The system separates planning from compilation so that the entire input graph can be validated before any output is produced.

### Phase 1: Plan

`create_plan` builds a `PlanNode` tree from a root directive and its source content. For each file it:

1. **Parses** — scans the source for ```` ```yaml embedm ```` blocks, producing a `Document` of `Fragment` objects.
2. **Validates directives** — calls `plugin.validate_directive()` for every `Directive` in the document. Errors are collected but do not stop planning.
3. **Checks sources** — verifies that each source file exists, is within size limits, is accessible, has not been seen before in the ancestor chain (cycle detection), and does not exceed the max recursion depth.
4. **Validates input** — for buildable source directives, loads the source content and calls `plugin.validate_input()`. The returned `artifact` is stored on the child `PlanNode`.
5. **Recurses** — if the source is itself a markdown file, `create_plan` is called again for the child, incrementing depth and extending the ancestor set.

The result is a fully populated tree of `PlanNode` objects. The plan phase never writes output.

### Phase 2: Compile

Compilation begins at the root node and is driven by the `FilePlugin`. For each document it:

1. **Resolves spans** — converts `Span` fragments to their source text slices.
2. **Runs compilation passes** — for each directive type in `plugin_sequence` order, all directives of that type in the fragment list are replaced by their plugin's compiled string output. All directives of type A are resolved before any of type B.
3. **Concatenates** — joins all remaining strings into the final output.

When a directive is compiled, its pre-built `PlanNode` (from the plan phase) is passed to `plugin.transform()` along with the current fragment list as `parent_document`. The plugin returns a string, which replaces the `Directive` fragment in the list.

## Error Model

### Status Levels

| Level | Meaning |
|-------|---------|
| `OK` | Validation passed; set on a node when no other statuses are collected. |
| `WARNING` | Something unexpected but non-blocking. Output is still produced. |
| `ERROR` | A directive cannot be compiled as specified. The user is prompted to continue or abort. |
| `FATAL` | A critical failure (e.g. circular dependency). Compilation of the affected file is aborted immediately. |

### Error Propagation

The plan tree carries errors at the node where they were detected. The `plan_tree` module provides helpers to walk the tree:

- `collect_tree_errors(root)` — returns all `ERROR` and `FATAL` statuses from every node.
- `tree_has_level(root, levels)` — returns `True` if any node has a status at the given level(s).

These are used by the orchestrator before compilation begins. If the tree has errors, the user is shown them and prompted to continue (unless `--accept-all` is set). A `FATAL` error bypasses the prompt and aborts compilation outright.

### Compile-time Errors

If a node's `document` is `None` (planning failed before a document could be built), the file plugin renders an inline error note in place of the directive rather than raising an exception. This means a partially broken document still compiles its healthy sections and clearly marks the failed ones.

## Document Model

### The Fragment Sequence

During compilation, the document is represented as a mutable list of `str | Directive` items (after spans have been resolved). This list is the `parent_document` that every plugin receives in its `transform()` call.

At the start of compilation the list interleaves text segments and unresolved `Directive` items, for example:

```
["# Introduction\n\n", <Directive type=file>, "\n## Section\n\n", <Directive type=toc>]
```

### Multi-pass Compilation

Each pass through `plugin_sequence` replaces all `Directive` items of one type with compiled strings. After the `file` pass the list might look like:

```
["# Introduction\n\n", "...embedded content...\n", "\n## Section\n\n", <Directive type=toc>]
```

Only after all preceding passes have run does the `toc` directive get replaced. At that point `parent_document` contains the compiled string output of every earlier plugin — the full text the toc will scan.

### Why plugin_sequence Order Matters

A plugin that reads `parent_document` (such as `toc` or `synopsis`) can only see string content from passes that have already completed. Directives of types that haven't run yet remain as `Directive` objects in the list and are invisible to text-scanning plugins.

Placing `toc_plugin`, `synopsis_plugin`, and `recall_plugin` last in `plugin_sequence` ensures that all embedded content — from files, data sources, tables — has been compiled into strings before these plugins scan for headings or text.

## Orchestration Flow

The `main()` function in `orchestration.py` ties everything together:

1. **Parse CLI arguments** — produce a `Configuration` object and validate it.
2. **Resolve config file** — auto-discover or load the explicit `embedm-config.yaml`; merge with CLI config.
3. **Build context** — load plugins into a `PluginRegistry`, create a `FileCache`, assemble an `EmbedmContext`.
4. **Dispatch** — route to file, directory, or stdin mode.
5. **Plan** — call `plan_file()` or `plan_content()` to build the `PlanNode` tree.
6. **Compile** — call `_compile_plan()` which checks the tree for errors, prompts the user if needed, then calls `_compile_plan_node()` to invoke the root plugin's `transform()`.
7. **Write** — apply line-ending normalisation and write to the configured output (file, directory, or stdout).
8. **Summarise** — emit the run summary to stderr.

Directory mode adds an outer loop over `.md` files. It also tracks embedded source paths to avoid compiling files that are dependencies of other files as standalone roots. Verify mode compiles normally but compares the result against the existing output file instead of writing.

## Infrastructure Services

### FileCache

`FileCache` is an LRU cache that mediates all file access.

- **Path access control** — only paths matching the `allowed_paths` glob list are readable; others return an error status.
- **Size limits** — files exceeding `max_file_size` are rejected. If the cache's total memory usage would exceed `memory_limit`, the least-recently-used entries are evicted.
- **Embed size** — `max_embed_size` is checked after compilation; any single embed result that exceeds the limit is replaced with an error note.
- **Event callback** — an optional `on_event` callback receives `(path, "hit"|"miss", elapsed_s)` for verbose cache reporting.

### Directive Parser

`parse_yaml_embed_blocks` scans markdown content for ```` ```yaml embedm ```` fences using a compiled regex, parses each block as YAML, and returns a list of `Fragment` objects. Relative `source` paths are resolved against the provided `base_dir` immediately so that all paths in the plan tree are absolute.

Source file content is always passed through the directive parser, even for non-markdown files. Non-markdown files typically contain no embedm blocks, so their fragment list is a single `Span` covering the whole content.
