# Circular Dependency Test

This test verifies that circular dependencies are properly detected and reported.

## Triggering the Cycle

```yaml
type: embed.file
source: file_a.md
```

## Expected Behavior

The embed above should fail with a circular dependency error because:
- test_circular.md embeds file_a.md
- file_a.md embeds file_b.md
- file_b.md tries to embed file_a.md (cycle!)
