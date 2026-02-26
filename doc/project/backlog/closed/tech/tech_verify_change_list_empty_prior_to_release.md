TECHNICAL IMPROVEMENT: Verify CL is empty prior to release
========================================
Created: 26/02/2026
Closed: 26/02/2026
Created by: `<Author>`

## Description

The Release Script can only run 

- if the user is on the main branch (soft protection, no one can commit to the main branch except for myself)

- there are no files in the change list of the main branch. (soft protection)


## Acceptance criteria

If neither or the acceptance criteria are fulfilled, the script will abort.

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
