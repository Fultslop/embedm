TECHNICAL IMPROVEMENT: `Plugin tutorial missing [build-system] section in pyproject.toml example`
========================================
Created: `27/02/26`
Closed: `<date>`
Created by: `Agent (plugin-validator skill)`

## Description

The plugin tutorial's `pyproject.toml` example omits the `[build-system]` section entirely.
Users unfamiliar with Python packaging must guess this value, and incorrect guesses
(e.g. `setuptools.backends.legacy:build`) produce an opaque pip error with no link back
to the tutorial. The correct value (`setuptools.build_meta`) should be included explicitly.

## Acceptance criteria

- `pyproject.toml` example in `plugin_tutorial.md` includes a `[build-system]` section
  with `requires = ["setuptools"]` and `build-backend = "setuptools.build_meta"`

## Comments

`27/02/26 Agent: discovered during plugin-validator skill run — pip install -e . failed on first attempt with BackendUnavailable: Cannot import 'setuptools.backends.legacy'`
