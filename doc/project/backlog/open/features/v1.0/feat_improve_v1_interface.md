FEATURE: Improve user interface
========================================
`<Optional Draft>`
`<Optional Planned release>`
Created: `<date>`
Closed: `<date>`
Created by: `<Author>`

## Description

The current output on the console

## Acceptance criteria

* -v / --verbose has a level associated with it:
  - 0: `silent`, assumed for cd/ci pipelines can read the exit code
    - no output to the console, 
    - no error messages if accept-all is set.  
  - 1: `minimal`, 
    - Title
    - no error messages if accept-all is set.  
    -  outcomes only  
  - 2: `default`
    - Title
    - top level md files being processed (in case of reading from directory) + status
    - error messages if accept-all is set.  
    - outcomes 
   -3: `verbose`
    - The excessive output of the current 'verbose' level, 

In all cases the user will still be prompted in case of errors (and accept all hasn't been turned on)

Discuss how we make all of these levels:
 - Easily readable
 - Understandable at a glance
 - Nice to look at, for as far as that's possible with console output
 - Easily parsable by tools

  * No functional changes

  * Update tests if needed

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`