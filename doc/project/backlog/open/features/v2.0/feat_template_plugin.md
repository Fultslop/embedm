FEATURE: Template plugin
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

A plugin that merges a markdown template file with a YAML or JSON data file, substituting `{{variable}}` placeholders with values from the data source. The output is the rendered template text, embedded inline.

Useful for stamping consistent blocks of text across multiple documents from shared metadata, and for generating repeated structures (release notes, component descriptions, team bios) from data files without duplication.

Directive definition:

```yaml embedm
type: template
template: ./templates/release_header.md
data: ./release.yaml
```

Template file example (`release_header.md`):
```markdown
## Release {{version}} — {{date}}

**Status:** {{status}}
```

Data file example (`release.yaml`):
```yaml
version: "1.2.0"
date: "2026-02-22"
status: "Stable"
```

### Behaviour

- `template` is a path to a markdown file containing `{{variable}}` placeholders.
- `data` is a path to a YAML or JSON file providing substitution values.
- All `{{key}}` occurrences in the template are replaced with their string values from the data file.
- Nested keys can be referenced with dot notation: `{{project.version}}`.
- Unknown placeholders → error caution block listing the missing keys.
- Unused data keys are silently ignored.

## Acceptance criteria

- All `{{variable}}` placeholders are substituted correctly
- Dot-notation nested key access works
- Unknown placeholder → error listing missing keys
- Data from YAML and JSON both work
- Unit tests and regression example included

## Comments

`22/02/2026 FS/Claude:` The `{{...}}` syntax avoids conflict with Jinja2/Mustache while being immediately recognisable. This plugin enables a pattern where project metadata lives in one YAML file and is stamped into any number of documents. Dependency on `json` plugin concept — could share the YAML/JSON loading layer.
