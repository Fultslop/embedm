FEATURE: Changelog plugin
========================================
Draft
Release v2.0
Created: 22/02/2026
Closed: `<date>`
Created by: FS

## Description

A plugin that parses a `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com) convention and embeds a specific version's section — or the latest release — into another document.

The common pattern: maintain a single `CHANGELOG.md` with all version history; embed only the latest release notes into your README automatically.

Directive definition:

```yaml embedm
type: changelog
source: ./CHANGELOG.md
version: latest          # or a specific version string like "1.2.0"
```

### Behaviour

- Parses `## [version]` or `## version` section headers from the source.
- `version: latest` selects the first (topmost) non-`[Unreleased]` section.
- A specific version string selects that exact section.
- The section body (everything until the next `##` heading) is embedded verbatim.
- Version not found → error caution block.

## Acceptance criteria

- `latest` selects the first non-unreleased version
- Specific version string resolves correctly
- Section body includes all sub-sections (Added, Fixed, etc.)
- Version not found → error caution block
- Unit tests and regression example with a sample CHANGELOG included

## Comments

`22/02/2026 FS/Claude:` Keep a Changelog is the de facto standard. Parsing is straightforward — just splitting on `## ` headings and matching version strings. No external dependencies.
