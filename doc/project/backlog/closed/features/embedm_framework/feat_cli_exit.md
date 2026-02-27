FEAT: CLI allow user to exit on the first error
=============================================
Draft
Created: 27/02/2026
Closed: 27/02/2026
Created by: FS

## Description

When running against a directory and errors occur, the user currently has no way to stop the entire process. Pressing 'n' only blocks the current file from being processed. If the user wants to stop, they have to press ctrl+C. 

We want the user to have the option to press 'x', 'Exit'  effectively calling 'exit'. ie this

```
Continue with compilation (yes/no/always)? [y/N/a]
```

should read

```
Continue with compilation (yes/no/always/exit)? [y/N/a/x]
```

## Acceptance criteria

- Prompt string updates to `Continue with compilation (yes/no/always/exit)? [y/N/a/x]`
- Pressing `x` or `exit` at the prompt exits the process with code 1
- `ctrl+C` maps to exit (code 1), consistent with `x`
- `--accept-all` (`-A`) is unaffected
- `--dry-run` is unaffected

## Comments

`27/02/26 FS: x/exit exits with code 1 (errors occurred). ctrl+C maps to EXIT.`