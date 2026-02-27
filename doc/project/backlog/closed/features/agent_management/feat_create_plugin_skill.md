FEATURE: Create plugin creation skill
========================================
Created: 27/02/2026
Closed: 27/02/2026
Created by: FS

## Description

Create and execute an `agent skill` which Claude Code can execute to test the `new plugin creation` workflow. Actions that Claude should be able to execute:

* Create a working directory.
* Read documentation available on github (https://github.com/Fultslop/embedm/blob/main/README.md)
* Setup a project.
* Install `embedm`.
* Create a simple `test.md` file.
* Execute embedm on the test file.
* Create a random trivial plugin (of the level of hello world)
* Install its project
* Build said plugin in python, 
* Add a `directive` to `test.md` to use its newly created plugin
* Run embedm on the test.md file and verify the output
* Collect structured documentation on its tasks and problems and improvements it encountered. It needs to be structured so we can track progress over time.

## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`27/02/2026 FS`: Added skill to the claude directory and `doc\project\agent_management\skills\plugin_validator.md`