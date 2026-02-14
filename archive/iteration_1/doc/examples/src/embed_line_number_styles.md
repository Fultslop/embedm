# Line Number Styling Examples

This document demonstrates the different line number styles available in embedm.

## Default Style

The default style uses GitHub's color scheme with a light background:

```yaml embedm
type: file
source: sample_code.py
line_numbers: html
```

The `line_numbers_style` property is optional. If omitted, the `default` theme is used automatically.

## Dark Style

The dark style features a dark background suitable for dark-themed documentation:

```yaml embedm
type: file
source: sample_code.py
line_numbers: html
line_numbers_style: dark
```

This theme uses high-contrast colors optimized for readability on dark backgrounds.

## Minimal Style

The minimal style provides simple, lightweight styling:

```yaml embedm
type: file
source: sample_code.py
line_numbers: html
line_numbers_style: minimal
```

This theme is ideal when you want code blocks to blend naturally with your document's existing styling.

## Custom CSS Theme

You can create your own custom CSS file for unique styling. This example uses a custom blue theme:

```yaml embedm
type: file
source: sample_code.py
line_numbers: html
line_numbers_style: custom-blue-theme.css
```

The custom CSS file ([custom-blue-theme.css](custom-blue-theme.css)) defines styles with:
- Light blue background (#e8f4f8)
- Bold blue line numbers with a vertical border
- Rounded corners and subtle shadow
- Larger padding for a spacious feel

**Note:** Custom CSS files are resolved relative to the markdown file's location. You can also use absolute paths if needed.

## Embedding Specific Lines with Styles

You can combine line number styles with region selection:

```yaml embedm
type: file
source: sample_code.py
region: L1-5
line_numbers: html
line_numbers_style: dark
```

## Text-based Line Numbers

For comparison, here's how text-based line numbers look (no styling customization available):

```yaml embedm
type: file
source: sample_code.py
region: L7-9
line_numbers: text
```

Note that `line_numbers_style` only applies to `line_numbers: html`, not `line_numbers: text`.
