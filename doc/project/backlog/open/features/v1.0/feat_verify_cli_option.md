FEATURE: CLI Verify option
========================================
Draft  
Release v1.0  
Created: 20/02/2026  
Closed: `<date>`  

## Description

Add a --verify CLI option which checks if any documents (dependencies of a md with embedded yamls) are out of date. Yields an error exit code when there are dependencies out of date. Enables CI pipelines to catch outdated docs.

This requires keeping track of the last_modified state of the file dependency vs the last_modified embedded in a snapshot file. Discuss how to best track this, maybe keep a manifest file in the compiled directory (can also be used to skip compile steps for files which haven't changed. Note skipping should be added to the --verbose output) ? 

The verfiy not run compile.

## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`