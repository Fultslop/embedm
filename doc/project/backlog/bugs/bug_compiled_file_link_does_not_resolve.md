BUG: Compiled file link does not resolve
========================================
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

Discuss.

Instead of the relative path from the `source md` file to the `embedded file`, the path should _probably_ be the relative path from the `compiled` file to the `source md` file + the relative path from source. 

Assume the `source md` sits in `./doc/src/test.md` and references two files `./file_1.txt` and `..\specs\spec.txt`. Assume the `compiled` file lands in `./doc/compiled`. The links in the compiled folder should point to `../src/./file_1.txt` and `../src/../specs/spect.txt` ie the relative path from `compiled` to `source` (`..\src`) + the relative path from `source` to the embedded.