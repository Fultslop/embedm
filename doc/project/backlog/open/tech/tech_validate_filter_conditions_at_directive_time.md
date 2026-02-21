TECHNICAL IMPROVEMENT: Validate filter conditions at directive-validate time
========================================
Created: 21/02/26
Closed: `<date>`

## Description

`_validate_filter()` in `src/embedm_plugins/table_plugin.py` checks that the `filter` option
parses as a valid JSON object, but does not inspect the condition strings within it:

```python
def _validate_filter(filter_str: str) -> list[Status]:
    try:
        parsed = json.loads(filter_str)
        if not isinstance(parsed, dict):
            return [Status(StatusLevel.ERROR, "'filter' must be a mapping...")]
        return []  # condition strings are not inspected
    except json.JSONDecodeError:
        ...
```

A condition string like `">= abc"` (non-numeric operand with a numeric operator) or `"@@ 30"`
(unrecognised operator that also isn't a bare string) will not be caught here. The user only
learns of the problem through unexpected output (no rows match), not through an error.

This is inconsistent with `select` and `order_by`, which are fully validated at
`validate_input` time (expression syntax + column existence) before the transformation runs.

**Proposed fix:** Extend `_validate_filter()` to parse each condition string using the same
`_FILTER_OP_PATTERN` regex that the transformer uses. If a condition uses an operator prefix
that is not in `_OPERATORS` (i.e., the pattern matches but the operator string is not a known
key), report an error. Note that the current `_FILTER_OP_PATTERN` only captures known
operators, so an unrecognised prefix is simply treated as an exact-match value — this is the
silent-failure case.

**Column existence for filter:** Cannot be validated at `validate_directive` time (no file
content). It is acceptable for filter to silently produce no matches when a column name does
not exist (consistent with SQL `WHERE` semantics). Only the condition syntax needs to be
validated.

**Scope:** `validate_directive` only — no changes to `validate_input` or the transformer.

**Consideration:** The filter string is serialised YAML passed as JSON. The condition values
are plain strings from user YAML. The validation operates on the deserialized `dict[str, str]`
already parsed by `_validate_filter()`.

## Acceptance criteria

* A directive with `filter: {age: ">= abc"}` (operator present, operand non-numeric) is
  accepted — this is valid syntax; numeric comparison simply falls back to string comparison
  at runtime. No change needed here.

* A directive with `filter: {age: "~~30"}` (unknown operator prefix) produces no error at
  validate_directive time (consistent with existing behaviour: treated as exact-match string).
  Document this as intended.

* If a future decision is made to treat unrecognised operator prefixes as errors, the
  acceptance criteria for that check should be added here.

* The existing `_validate_filter()` unit tests continue to pass.

* New unit tests cover valid filter maps with operators and bare-string conditions.

## Comments

**21/02/26 Claude:**

After closer analysis, `_FILTER_OP_PATTERN = re.compile(r"^(!=|<=|>=|<|>|=)\s*(.+)$")` only
captures conditions that start with a recognised operator. If the pattern does not match, the
transformer falls back to `operator_str = "="` (exact match). There is therefore no
unrecognised-operator code path that produces an error; the silent behaviour is by construction.

The real question is whether the current behaviour — silently treating `~~30` as an exact
string match — is acceptable to users. If yes, no code change is needed but the behaviour
should be documented. If no, the fix is to report an error when a condition string starts with
a non-word character but does not match `_FILTER_OP_PATTERN`.

**Recommend:** Discuss with FS before implementation.
