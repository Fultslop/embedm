FEATURE: Scratch directory to avoid duplicate compilations
==========================================================
Draft
Release 2.0
Created: 27/02/2026
Closed: `<date>`
Created by: ML

## Description

At the start of the application a list of all targeted md files should be collected (the `target list`). Files in the target list should never be compiled twice, because of the way the file_cache works. However this does not handle the double compilation which can happen when referencing files outside the target directory or its subdirectories. Eg:

  root/  
    some_other   
        file_c
  
    target_dir/
        file_a
            -> references file_c
        file_b
            -> references file_c
  
  file_c is not in the target_list and will be compiled twice. To avoid that the planner should collect a 'task' list of _all_ items to order. Currently the planner creates a DAG per file. Now it should create a DAG for all files in the current batch, then create a compilation set-list in order of dependencies. In the example above this would yield `[[c], [a, b]]`. file_c would be written to a temp 'scratch' directory in case it gets evicted from the file_cache. The file_cache would have to map 'file_c' -> 'scratch/file_c' internally. 

`<optional link to original / related feature(s)>`

`<optional dependencies on other feature(s)>`

## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`