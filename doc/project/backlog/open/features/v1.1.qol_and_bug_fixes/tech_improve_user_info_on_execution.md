TECHNICAL IMPROVEMENT: Improve user's understanding of current executing file
=============================================================================
Draft
Created: 27/02/2026
Closed: `<date>`
Created by: FS

## Description

During execution we only print what file has completed. The user doesn't see the current file that embedm is working on, creating the impression - in case of long operations - the preceding file is causing the delay. This is not a great user experience.

Moreover there is no sense of progress to the user. There are two things we can measure:

- In case of directories, we have information how many files we need to process, ie all the `*.md` files the user has specified. This is the `overall progress`.
- We also know, after planning, how many directives we need to compile. This is the `file progress`. 
- As we're compiling we can update both progress points and display them to the user. We will work towards a multithreading model where embedm can process multiple files/nodes at the same time, so the output needs to take that in account while still being compatible with all verbosity flags. Proposal for the progress output for the default verbosity flag while executing.

We establish three output states during execution

 * A start state
 * An exection state
 * A complete state

```
<COMPLETION LIST>
    <COMPLETION STATE> <TIME> <COMPLETED FILE 1> -> <OUTPUT_PATH> 

<TILE> <VERSION> <OVERALL PROGESS> <TIME>
 - <ACTIVE FILE 1>: <FILE_PROGRESS> <TIME>
 - <ACTIVE FILE 2>: <FILE_PROGRESS> <TIME>
 - ...
 - <ACTIVE FILE N>: <FILE_PROGRESS> <TIME>
 ...
```

Where the first line shows the number of completed files and below the progress of each file currently being worked on (in the current single threaded model that will be just 1 file). The file is printed contains the relative file path, followed by a two digit percentage (based on the number of nodes processed) and the duration. To not overflow the output, new output should overwrite the previous output from the line `Embedm [13/20]` on.

When a file completes or has a runtime error, it will output a new line above the current progress output, so the output forms a coherent list. Example


### Verbosity 0 silent

Unchanged, nothing will be shown.

### Verbosity 1 minimal

At the start:

``` shell
Embedm v1.1 [0/20]
```

At the end in case of all ok:

``` shell
Embedm v1.1 [20/20]
[Ok] 20/20, time: 3.4s 
exit code 0
```

At the end in case of errors:

``` shell
[ERR] 2.23s, rel_path/filename_b.md
`... exception trace`

Embedm v1.1 [20/20]
[Ok] 19/20, [ERROR] 1/20, time: 3.4s 
exit code 1
```

### Verbosity 2 default

**Step 1**
```
Embedm [0/3]
 - rel_path/filename_a.md: 0% (0.00s)
 - rel_path/filename_b.md: 0% (0.00s)
 - rel_path/filename_c.md: 0% (0.00s)
```

**Step 2**
```
Embedm [0/3]
 - rel_path/filename_a.md: 83% (0.10s)
 - rel_path/filename_b.md: 11% (0.10s)
 - rel_path/filename_c.md: 0% (0.00s)
```

**Step 3**
```
[OK] 1.22s, rel_path/filename_a.md -> rel_output_path/filename_a.md

Embedm [1/3]
 - rel_path/filename_b.md: 15% (1.22s)
 - rel_path/filename_c.md: 0% (0.00s)
```

**Step 4**
```
[OK] 1.22s, rel_path/filename_a.md -> rel_output_path/filename_a.md
[ERR] 2.23s, rel_path/filename_b.md
`exception trace`

Embedm [2/3]
 - rel_path/filename_c.md: 55% (1.00s)
```

**Step 5**
```
[OK] 1.22s, rel_path/filename_a.md -> rel_output_path/filename_a.md
[ERR] 2.23s, rel_path/filename_b.md
`exception trace`
[OK] 1.01s, rel_path/filename_c.md -> rel_output_path/filename_c.md

Embedm complete, 2 files ok, 1 error, total time: 3.4s 
exit code 1
```


This will require an event based logging system to deal with the future multithreaded scenarios. 



## Acceptance criteria

`<Optional: list of line description of tests to measure improvements>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
