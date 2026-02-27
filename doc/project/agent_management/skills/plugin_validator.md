---
name: plugin-validator
description: This skill creates, builds, and verifies a new python plugin for the embedm library. Use this when you need to test the plugin creation workflow or verify documentation accuracy.
---

# Skill: Embedm Plugin Validation

## Context
You are an expert developer testing the `embedm` ecosystem. Your goal is to simulate a user following the "New Plugin" workflow to find friction points.

## Instructions
1. **Setup**: Create a directory `plugin_test_DDMMYYYY_V` in the project's `./tmp` folder where the `_DDMMYYYY` postfix is the current date and `V` is an `autoincremental` number in case other directories exist.
2. **Install**: Install `embedm` into the newly created directory. *(This step is explicitly permitted within this skill — package management is otherwise restricted.)*
2. **Docs**: Read `https://github.com/Fultslop/embedm/blob/main/README.md` and specifically `https://github.com/Fultslop/embedm/blob/main/doc/manual/src/assets/tutorial/plugin_tutorial.md`
3. **Build**: 
   - Create a trivial Python plugin (e.g., "Hello World" or "Uppercase" directive).
   - Register the plugin in its own `pyproject.toml` or `setup.py`.
   - Install it into the current environment.
4. **Test**: Run `embedm` on a `test.md` using the new plugin's directive.
5. **Report**: See [Deliverables](#deliverables)
6: **Execution**: Always use the most direct CLI commands and avoid unnecessary file reads to conserve context.

## Error Management (3-Strike Rule)
- You have a **maximum of 3 attempts** to fix any specific error (e.g., build failure, import error).
- On the **3rd failed attempt** for the same issue: 
  - **STOP** immediately.
  - Do not try a 4th fix.
  - Proceed to the "Deliverables" section to report the failure.

## Deliverables
Create a `plugin_test_report.json` in the root directory. Use the structures below for the given outcome

### Success:

```json
{
  "timestamp": "2026-02-27T11:00:00Z",
  "status": "OK", 
  "summary": "Simple embed plugin created.",
  "encountered_problems": [
    {
      "attempt": 1,
      "action": "Initial install",
      "result": "ModuleNotFoundError: 'embedm.plugins'"
    },
    {
      "attempt": 2,
      "action": "Updated PYTHONPATH",
      "result": "Permission Denied on /usr/bin/..."
    }
  ],
  "feedback": [
        "The README doesn't specify that 'setuptools' is a requirement for plugin registration.",
        "Output was not helpful",
        "Step 3 unclear, propose rewriting to.."
  ]
}
```

### Failures:

Example

```json
{
  "timestamp": "2026-02-27T11:00:00Z",
  "status": "FAILED", 
  "attempts_made": 3,
  "last_action": "pip install ./my-plugin",
  "error_summary": "Circular dependency detected between embedm and local plugin.",
  "encountered_problems": [
    {
      "attempt": 1,
      "action": "Initial install",
      "result": "ModuleNotFoundError: 'embedm.plugins'"
    },
    {
      "attempt": 2,
      "action": "Updated PYTHONPATH",
      "result": "Permission Denied on /usr/bin/..."
    }
  ],
  "feedback": [
        "The README doesn't specify that 'setuptools' is a requirement for plugin registration."
  ]
}
```