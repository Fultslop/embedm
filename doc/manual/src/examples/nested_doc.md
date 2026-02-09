# Nested Documentation Example

This markdown file contains embeds that will be resolved when this file is embedded elsewhere.

## Code Example

Here's a Python function:

```yaml embedm
type: file
source: basic_example.py
lines: L4-6
```

## Another Section

This demonstrates recursive embedding - when this file is embedded using `type: file`, all the embeds within it will also be processed.

```yaml embedm
type: file
source: sections_example.py
lines: L9-14
title: "Function Two from sections_example.py"
```

This creates truly modular documentation!
