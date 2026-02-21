FEATURE: Directory Plugin
========================================
Draft  
Release v1.0  
Created: 20/02/26  
Closed: `<date>`  

## Description

Create a transformer plugin that takes a Directive where the source is a directory and turns it into a tree structure in the document.

Example

```yaml embedm
type: directory 
source: string, path/to/directory
include_files: file pattern, files to include. If not defined no file will be listed 
max_depth: int, max recursion depth. Default 3
```

## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`