TECHNICAL IMPROVEMENT: Move validation code from Table Transformer Execute
========================================
Created: 21/02/206
Closed: 22/02/206

## Description

The `execute` method of the table transformer (`src\embedm_plugins\table_transformer.py`) is doing a lot of validation tests before executing. For example:

```python
 rows, error = _parse_content(params.content, params.file_ext)
        if error:
            return error
```            

The transformer should only execute and return the resulting string, it should assume all input has been validated. Furthermore, by returing errors they may be hidden from the user. These errors should end up in the PlanNode's status. 

Therefore validation aspects should move to its own validation class with the plugin should focus orchestration between validation and transformation.

See `src\embedm\plugins\validation_base.py` for a proposal of the base class for Validation.

Implementing this approach as-is may result in double work. After all, for deep validation the respective validation base may need to parse or load content. To avoid/reduce the effect of double work, validation is allowed to capture and return relevant artifacts as expressed by the any return parameter.

**Example**

Take the following line from `src\embedm_plugins\table_transformer.py`:

```python
rows, error = _parse_content(params.content, params.file_ext)
```

This line and its should move to the a csv/tsv-table-validation and json-table-validation  class. It's up to the plugin to choose which one. The artifact returned is the row dictionary which can be added to Params of the transform.

The `_apply_pipeline` and `_render_table` is essentially the only thing the transformator has to do. 

To recap. The pipeline for plugins should, where applicable, be:

`Plugin -> Validation -> Transform`

Discuss.

## Acceptance criteria

* All validation logic / error reporting is removed from all transformers and moved to their corresponding Validation steps. 

* Unit/integration tests are updated.

* No failing regression tests.

* This should not affect other plugins yet. 

* Double work is avoided by returning an artefact from validation.

* Effective section added to claude.md to avoid these breaking architecture choices from recurring. Need input from Claude

## Comments 

**21/02/2026 Claude:**

ValidationBase.validate() return type is too loose

Any | list[Status] has no contract. The caller can't distinguish "success + artifact" from "failure + errors" without isinstance checks. A typed result wrapper would be cleaner:


@dataclass
class ValidationResult(Generic[TArtifact]):
    artifact: TArtifact | None
    errors: list[Status]
Then validate() always returns ValidationResult[TArtifact], which is unambiguous.

**21/02/2026 FS:** Good point

**21/02/2026 Claude:** How do validation errors reach PlanNode.status?

The spec says errors "should end up in PlanNode.status", but validate_directive() runs at plan time (no file content available). The new validation runs at transform time. The plugin would need to somehow inject errors into the plan node after the fact — but PlanNode fields look immutable. This needs clarification: do errors go to PlanNode.status, or do they still render as CAUTION blocks (which is the current, visible behavior)?

**21/02/2026 FS:**

Idea: Add a new step during planning: "validate_input" (and corresponding method to the Plugin) if validate_directive yields no errors. During this step the plugin either yields errors (which go into plannode) or an artifact (which is also added to plannode, to be used by the transform phase).

**21/02/2026 Claude:**
The note_no_table_content case

Currently the transformer returns a note string when rows are empty (after parsing OR after pipeline filtering). If this moves to validation, it changes meaning: empty-after-parse is arguably a file issue, but empty-after-filtering is a user query issue. They probably shouldn't be treated the same way.

**21/02/2026 FS:**

 Agreed. One is an error, the other one is an outcome of the user's filtering. It should just do what most databases do, yield a message to the effect of "no results"

 **21/02/2026 Claude:**

 A few design questions the spec should answer:

Is validate_input abstract (required on all plugins) or optional with a default no-op? Since most plugins don't need it (e.g. toc, hello_world), a default no-op with the base class returning None seems right — only plugins with content-level validation override it.

How does the artifact reach transform()? The natural path is plan_node.artifact: Any = None on PlanNode. The transformer receives the plan_node already, so no signature changes elsewhere. The downside is Any — but given PlanNode is shared across all plugins, that's probably unavoidable.

If validate_input returns errors, the planner should treat the node the same as it does for validate_directive errors: add to status, leave document = None. This means validate_input is called in the planner, after the file is cached, before recursion.

**21/02/2026 FS:**

Yes to all.