# Planned & Open issues

## High priority features / fixes

- Add manuals for toc / tables / layout / mermaid.

- Add a 'manual' which provides an overview of all manuals

- Create a 'synopsis' plugin and manual.

- Add a `--verify` mode that fails if compiled output is stale. Enables CI pipelines to catch outdated docs.

- Set up GitHub Actions CI (tests, coverage, regression snapshots).

- Publish to PyPI (`pip install embedm`).

- Move doc/examples to regression tests, where the current regression doesn't cover them

- Create a plugin to insert versions / build dates / ...

## Long term priority features / fixes

- Add a final "Transform"/"Output" phase mapping to md, html, pdf (?) or txt.

- Add caching, so embeddings won't need to be recompiled if not touched. 

- For large projects create a dependency tree, enabling a split to distribute embeddings in a directory over various threads.


- Watch mode (`--watch`) that recompiles when source files or embedded targets change.

- Symbol extraction for Rust, PHP, Kotlin, and TypeScript-specific syntax (decorators, traits, etc.).

- Diff-aware output that only re-embeds changed sections, useful for large doc sets in version control.

- A `--json` output mode for validation results, enabling integration with editors and build tools.

- Source URL annotation — optionally emit a comment or link back to the original file and line range.

- MkDocs / Docusaurus integration guides to capture organic search traffic from those ecosystems.

- Excel table insertion in a new project which uses this core project

## Undecided Features 

### Include embed

An `include` embed type for raw text insertion without code fences, useful for shared markdown fragments.

```
 the current file embed type already handles the main case: if you embed a .md file, it gets included recursively with its embeds resolved. So a shared markdown fragment already works — just name it .md.

The gap include would fill is narrow: inserting non-markdown files (.txt, .html snippets, partial templates) as raw text without code fences. In practice, you can work around this by naming your fragment .md regardless of its actual content.

It's not a bad idea, but it's solving a problem most users won't hit
```

### Glob patterns in `source`

Glob patterns in `source:` (e.g., `source: src/**/*.py, symbol: main`) for multi-file symbol search.

```
Sometimes you know the symbol name but not which file it's in. Instead of writing:


type: file
source: src/embedm/symbols.py
symbol: extract_symbol
You could write:


type: file
source: src/**/*.py
symbol: extract_symbol
EmbedM would search all matching files for that symbol and embed from whichever file contains it. Useful in large codebases where you don't want to hardcode the exact file path — if someone moves the function to a different module, the embed still resolves.

That said, it adds ambiguity (what if multiple files define the same symbol?) and complexity (scanning many files). It's a convenience feature, not essential — which is why it's in long-term. The current approach of specifying the exact file is more explicit and predictable.
```
#### Comments

```
Currently out of scope. 
It's an interesting thought and therefore worth capturing but I'd leave that responsibility of knowing what file it is to the user. Also may affect performance negatively.
```



## Completed features

- 11/02/26 Fix TOC generator to skip `#` lines inside fenced code blocks.

- 11/02/26 Improve README with a "Why EmbedM?" section and a concise before/after example.

- 11/02/26 Add a feature to the ToC plugin to select depth of sections. This should enable pruning less relevant sections.

- class , function region, test java, js, c++, c, rust

- extend symbols for rust, go, php, typescript, kotlin -- example for one

- does it support interfaces
- add simplified mermaid
- add code coverage
- increase code coverage
- Add manual to regresion snapshot (maybe split directory)
- Revisit eating dogfood
- failures when symbol not found / doesn't compile
- deal with cases where a closing } is inside a comment or string
- deal with overloaded functions eg doSm(int) and doSm(bool)
- deal with inner classes or files having multiple classes with the same function name
- whitelist directory

