# Regression Tests

This directory contains regression tests for EmbedM that compare actual output against expected snapshots. These tests help catch unintended changes to output formatting, TOC generation, table conversion, and other features.

## Directory Structure

```
tests/regression/
├── sources/           # Input markdown files with embeds
│   ├── *.md          # Test markdown files
│   ├── circular_deps/ # Circular dependency test cases
│   │   ├── file_a.md
│   │   ├── file_b.md
│   │   └── test_circular.md
│   └── data/          # Supporting files (CSV, JSON, Python)
│       ├── sample.py
│       ├── sample.csv
│       └── sample.json
├── snapshots/         # Expected output (committed to git)
│   ├── *.md
│   └── circular_deps/
│       └── *.md
├── actual/            # Actual output during tests (gitignored)
│   └── ...            # Generated during tests, deleted if matches
└── README.md          # This file
```

## How Regression Tests Work

1. **Process**: Each source file in `sources/` is processed through EmbedM
2. **Write**: Output is written to `actual/`
3. **Compare**: Output is compared byte-for-byte with `snapshots/`
4. **Clean**: Matching files are deleted from `actual/`
5. **Fail**: If any differences remain, the test fails

## Running Regression Tests

```bash
# Run all regression tests
pytest tests/test_regression.py -v

# Run specific regression test
pytest tests/test_regression.py::TestRegression::test_toc_generation_regression -v

# Run with full test suite
pytest tests/
```

## When Tests Fail

If regression tests fail, it means the output has changed. This could be:

1. **Unintended change** (regression) - Fix the code
2. **Intentional change** (new feature/bug fix) - Update snapshots

### Investigating Failures

When tests fail, inspect the `actual/` directory to see the differences:

```bash
# View actual output
cat tests/regression/actual/toc_generation.md

# Compare with snapshot
diff tests/regression/actual/toc_generation.md tests/regression/snapshots/toc_generation.md

# Or use your favorite diff tool
code --diff tests/regression/actual/toc_generation.md tests/regression/snapshots/toc_generation.md
```

## Updating Snapshots

After verifying that changes are intentional and correct:

```bash
# Update all snapshots
python scripts/update_regression_snapshots.py

# Review changes
git diff tests/regression/snapshots/

# Commit updated snapshots
git add tests/regression/snapshots/
git commit -m "Update regression test snapshots"
```

**IMPORTANT:** Always review snapshot changes before committing! Don't blindly update snapshots to make tests pass.

## Test Cases

### Basic Features

- **simple_file_embed.md** - Basic file embedding
- **toc_generation.md** - TOC generation (H1 exclusion, no self-reference)
- **table_csv.md** - CSV to markdown table conversion
- **table_json.md** - JSON to markdown table conversion
- **line_numbers.md** - File embedding with line numbers

### Edge Cases

- **circular_deps/test_circular.md** - Circular dependency detection
  - Tests that infinite loops are properly detected and reported
  - Verifies error message format

## Adding New Regression Tests

1. **Create source file** in `tests/regression/sources/`
   ```markdown
   # My New Feature Test

   ```yaml
   type: embed.newfeature
   source: data/example.txt
   ```
   ```

2. **Add supporting files** to `tests/regression/sources/data/` if needed

3. **Generate snapshot**
   ```bash
   python scripts/update_regression_snapshots.py
   ```

4. **Verify output** looks correct
   ```bash
   cat tests/regression/snapshots/my_new_feature.md
   ```

5. **Run tests**
   ```bash
   pytest tests/test_regression.py -v
   ```

6. **Commit**
   ```bash
   git add tests/regression/sources/my_new_feature.md
   git add tests/regression/snapshots/my_new_feature.md
   git commit -m "Add regression test for new feature"
   ```

## Benefits

- **Catch regressions early**: Immediately detect when output changes
- **Document expected behavior**: Snapshots serve as living documentation
- **Fast feedback**: File comparison is very fast
- **Easy debugging**: Failed tests leave actual files for inspection
- **Confidence in refactoring**: Change internals without changing output

## Notes

- The `actual/` directory is gitignored
- Only `sources/` and `snapshots/` are committed to git
- Tests clean up matching files automatically
- Failed tests leave differing files in `actual/` for inspection
