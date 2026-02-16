# Error Handling Guidelines

## Two categories of errors

### Coding errors (internal contract violations)

A component receives data that should be impossible if the upstream code is correct.

- **Mechanism:** `assert` with a descriptive message
- **Result:** crash immediately
- **Examples:**
  - Transformer receives `plan_node.document is None` (planner guarantees it)
  - Plugin called with wrong directive type (registry guarantees dispatch)
  - Fragment type not in the union (parser guarantees it)
  - FileCache called with a path that was already validated

### Input errors (external data failures)

Anything that crosses the system boundary: file paths from markdown, CLI arguments, file content from disk.

- **Mechanism:** `Status` collection on the plan node
- **Result:** continue processing, mark the node, present errors
- **Examples:**
  - File does not exist
  - File exceeds size limit
  - Invalid YAML in embedm block
  - Unknown directive type (no plugin registered)
  - Circular dependency
  - Max recursion exceeded
  - Invalid directive options (plugin validation)

## Boundary rule

> Could a user cause this by writing bad markdown or passing bad arguments?
> If yes: collect as Status. If no: assert.

## Error flow

### Planning stage

Collect all errors across the tree. Each `PlanNode` carries its own `status` list. Child errors do not fail the parent. After planning, present all errors to the user. The user is asked to continue or abort. (For directory mode: continue/abort/continue-all.)

### Compilation stage

Nodes with error/fatal status render as a Markdown note block in the output instead of resolving via a plugin:

```markdown
> [!WARNING]
> embedm: failed to resolve directive (file not found: './missing.md')
```

Runtime/compilation errors are also rendered inline in the output.

## Preconditions

Use `assert` at public method entry points where an earlier pipeline stage established a guarantee:

```python
def execute(self, params: EmbedmFileParams) -> str:
    assert params.plan_node.document is not None, "transformer requires a planned document"
```

Plain `assert` with a message is sufficient. No custom precondition framework.
