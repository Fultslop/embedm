# Include lines

```yaml embedm
type: file
title: single line L10 (no line numbers)
source: hello.py
region: L10
```

```yaml embedm
type: file
title: lines starting from L5 (text line numbers)
source: hello.py
region: L5-
line_numbers: text
```

```yaml embedm
type: file
title: lines from L5-L10 (html line numbers)
source: hello.py
region: L5-L10
line_numbers: html
```