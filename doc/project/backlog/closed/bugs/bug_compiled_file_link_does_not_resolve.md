BUG: Compiled file link does not resolve
========================================
Draft  
Created: 20/02/2026  
Closed:  

## Description

The fileplugin allows for the property 'link' to show a link above the embedded file. When the user clicks this link it should take them to the file. This currently doesn't work because the compiled md file doesn't point to the actual embedded file.

## Replication

Use Embedm to compile the input file below. This does not match the expected outcome.

**Input:**

Markdown file, test.md:

```yaml embedm
type: file
source: ./path/relative/to/test/md/some_file.txt
link: True
```

**Output**

[some_file.txt](./path/relative/to/test/md/some_file.txt)
```txt
some_file.txt data
```

**Expected**

Instead of the relative path from the `source md` file to the `embedded file`, the path should _probably_ be the relative path from the `compiled` file to the `source md` file + the relative path from source. 

Assume the `source md` sits in `./doc/src/test.md` and references two files `./file_1.txt` and `..\specs\spec.txt`. Assume the `compiled` file lands in `./doc/compiled`. The links in the compiled folder should point to `../src/./file_1.txt` and `../src/../specs/spect.txt` ie the relative path from `compiled` to `source` (`..\src`) + the relative path from `source` to the embedded.

The compiled directory is provided / can be derived from the cli:

- in case of compiling to directories via the --dir option
- in case of compiling to a single file, the path of the output file -o

This needs to be propagated to the transformer via the `FileParams`.

## Comments

21/02/2026 Claude:  
"On the proposed approach:

The spec describes the solution as:

relative path from compiled to source + relative path from source to embedded

This is the right mental model but the wrong implementation approach. It produces paths like ../src/./file_1.txt that need normalization. There's a simpler formulation that avoids this entirely:

relative path from compiled_dir to abs(embedded_file)

This works because after planning, source_path passed to _relative_link_path is already absolute. The fix is just changing what base_dir is passed in — from the source md's directory to the compiled output directory. os.path.relpath(source_path, compiled_dir) does it in one step, normalized automatically.

One concern worth addressing in the spec: the --dir and -o cases produce different types of "compiled location":

--dir: the compiled directory is known upfront and applies to all files
-o: the compiled path is a single file, so compiled_dir = dirname(-o)
Both cases reduce to a compiled_dir string, so propagating that via FileParams is clean. The spec should make this explicit — FileParams gets a compiled_dir: str, and _relative_link_path receives that instead of base_dir.

Summary: The approach is right. I'd just reframe the expected output as relpath(abs_embedded, compiled_dir) rather than path concatenation, and confirm whether source_path is always absolute at transform time (which would simplify the implementation significantly)."

21/02/2026 ML: Approved, let's take that approach.