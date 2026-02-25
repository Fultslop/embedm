TECHNICAL IMPROVEMENT: Create Precommit on-push GH action
========================================
Created: 25/02/2026
Closed: 25/02/2026
Created by: FS

## Description

Create a GH action which runs on push pr, runs the entire pre-commit testsuite before a pull request can be approved

 ie

```yaml
    - name: Run tests
      run: uv run pytest

    - name: Run lint
      run: make lint

    - name: Run static-Analysis
       run: make static-analysis
```

## Acceptance criteria

* A new gh action is added to `python\embedm\.github\workflows` which runs test, lint and static analysis. 

* No pr can be approved without these actions succeeding

* It (probably) should NOT run update snapshots (responsibility of the user)

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
