TECHNICAL IMPROVEMENT: Tag application is out of order
========================================
`<Optional Draft>`
Created: `<date>`
Closed: `<date>`
Created by: `<Author>`

## Description

Right now the release is tagged and then committed which will trigger a release build.
The problem with this is that the versions headers in the various documents are incorrect and the `uv.lock` will show the wrong version.

What should happen is:

* the pyproject.toml version is updated (as it is now)
* `make snapshots` is run
* IF `make snapshots` fails for some reason, the pyproject.toml version is reverted and the process exits.
* IF `make snapshots` succeeds whatever is on the changelist is committed and pushed to main (this should include the uv.lock)
* Only then the git version is tagged and a release build is kicked off

## Acceptance criteria



## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
