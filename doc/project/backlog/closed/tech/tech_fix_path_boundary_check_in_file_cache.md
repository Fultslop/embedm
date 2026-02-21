TECHNICAL IMPROVEMENT: Fix path boundary check in FileCache
========================================
Created: 21/02/26
Closed: `<date>`
Created by: Claude

## Description

The spec states: *"Embedm can ONLY read and write from and to paths that the user has explicitly defined."*

`_is_path_allowed()` in `src/embedm/infrastructure/file_cache.py` enforces this with a prefix check:

```python
if resolved.startswith(allowed_resolved):
    return True
```

This check has a boundary flaw. If an allowed path is `C:\Users\project`, then
`C:\Users\project_evil\secret.txt` also passes because it is a string prefix match,
not a directory boundary match. The character immediately after the prefix is not checked.

**Example:**
- `allowed_paths = ["C:\\Users\\project"]`
- `resolved = "C:\\Users\\project_evil\\secret.txt"`
- `resolved.startswith("C:\\Users\\project")` → `True` (incorrect)

**Mitigating context:** Production orchestration always passes `["./**"]` as `allowed_paths`,
which routes through `fnmatch`, not `startswith`. The bug is therefore currently only
reachable via direct `FileCache` construction (e.g., in tests or by future callers). However,
the implementation is incorrect and violates the spec guarantee, so it must be fixed.

**Fix:** After the prefix check, verify the next character in the resolved path is a separator
(or the paths are equal). On Windows both `/` and `\` must be accepted since `Path.resolve()`
normalises to `\` but defensive code should accept both.

```python
sep = os.sep
if resolved.startswith(allowed_resolved) and (
    len(resolved) == len(allowed_resolved)
    or resolved[len(allowed_resolved)] in (sep, "/", "\\")
):
    return True
```

## Acceptance criteria

* A test with `allowed_paths=["/tmp/project"]` confirms that `/tmp/project_evil/file.txt`
  is rejected while `/tmp/project/file.txt` is accepted.

* A test confirms that the allowed path itself (exact match, no trailing separator) is accepted.

* A test confirms that a file directly inside the allowed path (one level) is accepted.

* All existing `FileCache` tests continue to pass.

* No failing regression tests.
