TECHNICAL IMPROVEMENT: Move validation code from Table Transformer Execute
========================================
Draft
Created: 21/02/206
Closed: `<date>`

## Description

The `execute` method of the table transformer (`src\embedm_plugins\table_transformer.py`) is doing a lot of validation tests before executing. For example:

```python
 rows, error = _parse_content(params.content, params.file_ext)
        if error:
            return error
```            

The transformer should only execute and return the resulting string. Validation is should move to its own validation class. The plugin should focus orchestration.

See `src\embedm\plugins\validation_base.py` for a proposal of the base class.

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
