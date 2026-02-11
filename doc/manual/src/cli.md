# CLI Reference

Command-line interface reference for EmbedM.

## Table of Contents

```yaml embedm
type: toc
```

## Synopsis

```
embedm SOURCE [OUTPUT] [options]
```

EmbedM processes markdown files containing embed directives and produces compiled output with all embeds resolved.

## Positional Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `SOURCE` | Yes | Source markdown file or directory to process |
| `OUTPUT` | No | Output file or directory. Defaults to `SOURCE.compiled.md` for single files |

When `SOURCE` is a directory, EmbedM looks for an `embedm_config.yaml` file in that directory. If found, it uses the config's `output.directory` setting. If not found, it prompts to create one.

**Single file** — creates `input.compiled.md`:

```
embedm input.md
```

**Single file with explicit output:**

```
embedm input.md output.md
```

**Directory mode** — processes all `.md` files:

```
embedm docs/src/ docs/compiled/
```

## Processing Limits

These flags override values from `embedm_config.yaml` and built-in defaults. Set any limit to `0` to disable it.

| Flag | Default | Description |
|------|---------|-------------|
| `--max-file-size SIZE` | `1MB` | Maximum input file size |
| `--max-recursion N` | `8` | Maximum recursion depth for embedded markdown |
| `--max-embeds N` | `100` | Maximum embed directives per file |
| `--max-output-size SIZE` | `10MB` | Maximum compiled output file size |
| `--max-embed-text SIZE` | `2KB` | Maximum size of a single embedded text snippet |

Size values accept bytes (`1024`), kilobytes (`1KB`, `1K`), megabytes (`1MB`, `1M`), and gigabytes (`1GB`, `1G`).

### Precedence

Limit values are resolved in this order (first match wins):

1. CLI flag (e.g., `--max-file-size 5MB`)
2. Config file (`embedm_config.yaml`)
3. Built-in default

### Limit Examples

Allow larger files and deeper recursion:

```
embedm docs/src/ --max-file-size 5MB --max-recursion 10
```

Disable the embed-per-file limit:

```
embedm input.md --max-embeds 0
```

Unlimited recursion:

```
embedm input.md --max-recursion 0
```

## Sandbox Options

EmbedM restricts file access to prevent embed directives from reading files outside the project. This protects against path traversal attacks where a malicious markdown file uses `source: ../../../../etc/passwd` to exfiltrate system files.

| Flag | Description |
|------|-------------|
| `--allow-path DIR [DIR ...]` | Additional directories to allow file access from |
| `--no-sandbox` | Disable the file access sandbox entirely |

### How the Sandbox Root Is Determined

EmbedM detects the sandbox root automatically, trying these sources in order:

| Priority | Source | Description |
|----------|--------|-------------|
| 1 | Git repository | Runs `git rev-parse --show-toplevel` from the source file's directory |
| 2 | Config directory | Uses the directory containing `embedm_config.yaml` |
| 3 | Working directory | Falls back to the current working directory |

The sandbox root and how it was detected are shown in the validation output:

```
Sandbox: C:\Users\me\project (git repository root)
```

### Monorepo Support

In a monorepo, the git root covers all projects automatically. If your source files are in `repo/projectA/doc/` and you need to embed from `repo/projectB/src/`, no extra flags are needed — both are under the same git root.

### Allowing Additional Paths

Use `--allow-path` to grant access to directories outside the sandbox root.

Allow access to a shared assets directory:

```
embedm docs/src/ --allow-path /shared/assets
```

Allow multiple extra directories:

```
embedm docs/src/ --allow-path /shared/assets /other/lib
```

### Disabling the Sandbox

Use `--no-sandbox` to disable file access restrictions entirely:

```
embedm input.md --no-sandbox
```

### Security Notes

- The sandbox cannot be bypassed with `--force`. Sandbox violations always block processing.
- Symlinks are resolved before path checking, so a symlink pointing outside the sandbox is caught.
- On Windows, path comparisons are case-insensitive.
- The sandbox is designed to prevent accidental or malicious file access, not to be a security boundary for untrusted environments.

## General Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Validate only — do not write any output files |
| `--force` | Continue processing despite validation errors. Warnings are embedded in the compiled output as callouts |
| `--verbose`, `-v` | Show detailed output including full error tracebacks |

### Dry Run

Use `--dry-run` to validate all embeds without writing output:

```
embedm docs/src/ --dry-run
```

This runs the full validation phase (file existence, size limits, circular dependency detection, region/symbol validation) and reports all errors, but does not produce compiled files.

### Force Mode

By default, EmbedM exits with an error if validation finds problems. Use `--force` to proceed anyway — errors are embedded in the output as GitHub-style callout blocks:

```
embedm input.md --force
```

Errors in the compiled output look like:

```markdown
> [!CAUTION]
> **Embed Error:** File not found: `missing.py`
```

Note: `--force` does **not** bypass sandbox violations. Those always block processing.

## Configuration File

When processing a directory, EmbedM looks for `embedm_config.yaml` in the source directory. The config file sets default limits and output options:

```yaml
limits:
  max_file_size: "1MB"
  max_recursion: 8
  max_embeds_per_file: 100
  max_output_size: "10MB"
  max_embed_text: "2KB"

output:
  directory: "compiled"

plugins: "*"
```

CLI flags always override config file values. See the Precedence section under Processing Limits.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Validation errors or processing failure |
| `130` | Interrupted by user (Ctrl+C) |
