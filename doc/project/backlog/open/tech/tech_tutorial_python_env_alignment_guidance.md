TECHNICAL IMPROVEMENT: `Plugin tutorial gives no guidance on Python environment alignment`
========================================
Created: `27/02/26`
Closed: `<date>`
Created by: `Agent (plugin-validator skill)`

## Description

The tutorial instructs users to "install into the current environment" without clarifying
that the plugin must be installed into the same Python environment that runs the `embedm`
CLI. In dev setups where embedm is installed in a project `.venv`, the `embedm` on PATH
and the system `pip` resolve to different environments. The plugin installs into one;
embedm loads from the other. The result is a silent failure with no actionable error.

A note guiding users to verify environment alignment (e.g. confirm `which embedm` and
`which pip` resolve to the same Python) would prevent this class of failure.

## Acceptance criteria

- Tutorial includes a note or step instructing users to verify that the `embedm` CLI
  and `pip install` target the same Python environment before installing the plugin

## Comments

`27/02/26 Agent: discovered during plugin-validator skill run — plugin installed into global Python while embedm ran from project .venv; plugin was silently skipped`
