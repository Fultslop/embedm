# File A

This file embeds File B, which creates a circular dependency.

## Embedding File B

# File B

This file embeds File A, completing the circular dependency.

## Embedding File A

# File A

This file embeds File B, which creates a circular dependency.

## Embedding File B

> [!CAUTION]
> **Embed Error:** Infinite loop detected! `file_b.md` is trying to embed a parent.

End of File A.


End of File B.


End of File A.
