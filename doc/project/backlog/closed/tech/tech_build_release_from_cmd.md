TECHNICAL IMPROVEMENT: Build release from the command line
==========================================================
Created: 25/02/2026
Closed: 25/02/2026
Created by: FS

## Description

Create a script + workflow to build releases from the command line.

- Assume `gh auth login` was succesfull and complete
- There are no items on the ChangeList (see todo)

Run from project root as:  
    uv run python scripts/create_release.py |version| |--dry-run|

# eg: uv run python scripts/create_release.py 3.4.5 --dry-run

* **TODO** verify prior to making a release
* **TODO** increase the version of the pyproject, run build snapshots, then commit / push changes, then tag the current version and trigger a release build

## Acceptance criteria

* The script will invoke git tag both for local and remote
* The script will invoke a new gh action which will trigger a release build
* If no version is provided, the version will auto increase with +0.0.1
* If a version is provided the project will be set to that version
* Optional --dry-run will only show what it intends to do

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
