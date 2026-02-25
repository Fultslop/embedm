# Command-Line Interface

version 0.9.8

embedm is invoked from the terminal. Input can be a file, a directory, or piped via stdin. Output goes to a file, a directory, or stdout.

  - [Synopsis](#synopsis)
  - [Input Modes](#input-modes)
    - [File](#file)
    - [Directory](#directory)
    - [Stdin](#stdin)
  - [Options](#options)
    - [-o, --output-file FILE](#o---output-file-file)
    - [-d, --output-dir DIR](#d---output-dir-dir)
    - [-c, --config FILE](#c---config-file)
    - [-A, --accept-all](#a---accept-all)
    - [-n, --dry-run](#n---dry-run)
    - [--verify](#verify)
    - [-v, --verbose [LEVEL]](#v---verbose-level)
    - [--init [DIR]](#init-dir)
  - [Input Detection](#input-detection)
  - [Exit Codes](#exit-codes)
  - [Constraints](#constraints)

## Synopsis

```
embedm [input] [-o FILE] [-d DIR] [-c CONFIG]
       [-A] [-n] [--verify] [-v [LEVEL]] [--init [DIR]]
```

## Input Modes

### File

Pass a single markdown file. Output goes to stdout unless `-o` or `-d` is also given.

```
embedm content.md
embedm content.md -o compiled.md
```

### Directory

Pass a directory path, a `*` glob, or a `**` glob. embedm expands the pattern to all `.md` files, compiles each one, and writes results to the output directory (mirroring the source structure).

```
embedm ./src -d ./out
embedm "./*" -d ./out
embedm "./**" -d ./out
```

Files that appear as embedded dependencies of other files in the same run are skipped as standalone roots.

### Stdin

Omit the input argument and pipe content in. Output goes to stdout unless `-o` is given.

```
cat content.md | embedm
cat content.md | embedm -o compiled.md
```

## Options

### -o, --output-file FILE

Write compiled output to FILE. Valid for file and stdin modes. Cannot be combined with `-d`.

```
embedm content.md -o compiled/content.md
```

### -d, --output-dir DIR

Write compiled output to DIR, mirroring the source directory structure. Required for directory mode; also usable with file mode to route output into a directory.

```
embedm ./src -d ./compiled
```

### -c, --config FILE

Load configuration from FILE instead of auto-discovering `embedm-config.yaml`. See [Configuration](./configuration.md) for the file format.

```
embedm content.md -c my-config.yaml
```

### -A, --accept-all

Continue compiling when errors are encountered, without prompting. Errors are still reported at verbosity level 2 (default) and above. At verbosity 0 or 1, errors are suppressed and a summary hint is shown instead.

```
embedm ./src -d ./out -A
```

### -n, --dry-run

Compile without writing any output files. Results are printed to stdout. Useful for previewing output or checking for errors.

```
embedm content.md -o out.md -n
```

Cannot be combined with `--verify`.

### --verify

Compile and compare the result against the existing output file. Prints `UP-TO-DATE` or `STALE` for each file and exits with code 1 if any file is stale. Does not write files. Requires `-o` or `-d`.

```
embedm content.md --verify -o compiled.md
embedm ./src --verify -d ./compiled
```

Cannot be combined with `--dry-run`.

### -v, --verbose [LEVEL]

Set the verbosity level (0–3). Default is 2 when the flag is omitted; passing `-v` without a number sets level 3.

| Level | Output |
|-------|--------|
| 0 | Silent — no stderr output at all |
| 1 | Minimal — summary line only |
| 2 | Default — summary line; per-file progress in directory mode; errors shown |
| 3 | Verbose — configuration, plugin list, plan tree, timing, cache events |

```
embedm content.md -v          # level 3
embedm content.md -v 1        # level 1
embedm content.md --verbose 0 # silent
```

### --init [DIR]

Generate a default `embedm-config.yaml` in DIR (defaults to the current directory if DIR is omitted). Exits immediately after writing the file without compiling anything.

```
embedm --init
embedm --init ./my-project
```

## Input Detection

Directory mode is activated automatically when:
- the input path contains `*` (glob pattern), or
- the input path is an existing directory on disk.

Otherwise file mode is used. Stdin mode activates when no input argument is provided and stdin is not a terminal.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | One or more errors occurred, or `--verify` found stale files |

## Constraints

- `-o` and `-d` are mutually exclusive.
- `-o` cannot be used with directory input.
- `--verify` requires `-o` or `-d`.
- `--verify` and `--dry-run` cannot be combined.
- `-v LEVEL` must be in the range 0–3.
