# Circular Dependency Test

This test verifies that circular dependencies are properly detected and reported.

## Triggering the Cycle

# File A

This file embeds File B, which creates a circular dependency.

## Embedding File B

# File B

This file embeds File A, completing the circular dependency.

## Embedding File A

> [!CAUTION]
> **Embed Error:** Infinite loop detected! `file_a.md` is trying to embed a parent.

End of File B.


End of File A.


## Expected Behavior

The embed above should fail with a circular dependency error because:
- test_circular.md embeds file_a.md
- file_a.md embeds file_b.md
- file_b.md tries to embed file_a.md (cycle!)
