# Line Numbers Test

This tests file embedding with line numbers.

## Specific Function

```yaml
type: embed.file
source: data/sample.py
lines: L6-15
line_numbers: text
```

## Full File with Line Numbers

```yaml
type: embed.file
source: data/sample.py
line_numbers: text
```

## Line Number Styling Examples

This document demonstrates the different line number styles available in embedm.

### Default Style

The default style uses GitHub's color scheme with a light background:

```yaml
type: embed.file
source: data/sample.py
line_numbers: html
```

The `line_numbers_style` property is optional. If omitted, the `default` theme is used automatically.

### Dark Style

The dark style features a dark background suitable for dark-themed documentation:

```yaml
type: embed.file
source: data/sample.py
line_numbers: html
line_numbers_style: dark
```

This theme uses high-contrast colors optimized for readability on dark backgrounds.

### Minimal Style

The minimal style provides simple, lightweight styling:

```yaml
type: embed.file
source: data/sample.py
line_numbers: html
line_numbers_style: minimal
```

This theme is ideal when you want code blocks to blend naturally with your document's existing styling.

### Custom CSS Theme

You can create your own custom CSS file for unique styling. This example uses a custom blue theme:

```yaml
type: embed.file
source: data/sample.py
line_numbers: html
line_numbers_style: ./data/custom-blue-theme.css
```

The custom CSS file ([custom-blue-theme.css](custom-blue-theme.css)) defines styles with:
- Light blue background (#e8f4f8)
- Bold blue line numbers with a vertical border
- Rounded corners and subtle shadow
- Larger padding for a spacious feel

**Note:** Custom CSS files are resolved relative to the markdown file's location. You can also use absolute paths if needed.

### Embedding Specific Lines with Styles

You can combine line number styles with region selection:

```yaml
type: embed.file
source: data/sample.py
region: L1-5
line_numbers: html
line_numbers_style: dark
```

### Text-based Line Numbers

For comparison, here's how text-based line numbers look (no styling customization available):

```yaml
type: embed.file
source: data/sample.py
region: L7-9
line_numbers: text
```

Note that `line_numbers_style` only applies to `line_numbers: html`, not `line_numbers: text`.
