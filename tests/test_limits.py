"""Unit tests for safety limits and validation features."""

import unittest
import tempfile
import os
from pathlib import Path

from embedm.models import Limits, ValidationError, ValidationResult, EmbedDirective
from embedm.discovery import (
    discover_files,
    discover_embeds_in_file,
    build_dependency_graph,
    detect_cycles,
    calculate_max_depth
)
from embedm.validation import validate_all
from embedm.resolver import resolve_content, ProcessingContext


class TestLimitsModel(unittest.TestCase):
    """Test the Limits data model."""

    def test_parse_size_bytes(self):
        """Test parsing plain byte values."""
        self.assertEqual(Limits.parse_size('1024'), 1024)
        self.assertEqual(Limits.parse_size('2048'), 2048)

    def test_parse_size_kilobytes(self):
        """Test parsing kilobyte values."""
        self.assertEqual(Limits.parse_size('1KB'), 1024)
        self.assertEqual(Limits.parse_size('1K'), 1024)
        self.assertEqual(Limits.parse_size('2KB'), 2048)

    def test_parse_size_megabytes(self):
        """Test parsing megabyte values."""
        self.assertEqual(Limits.parse_size('1MB'), 1024 * 1024)
        self.assertEqual(Limits.parse_size('1M'), 1024 * 1024)
        self.assertEqual(Limits.parse_size('5MB'), 5 * 1024 * 1024)

    def test_parse_size_gigabytes(self):
        """Test parsing gigabyte values."""
        self.assertEqual(Limits.parse_size('1GB'), 1024 * 1024 * 1024)
        self.assertEqual(Limits.parse_size('1G'), 1024 * 1024 * 1024)

    def test_parse_size_invalid(self):
        """Test parsing invalid size formats."""
        with self.assertRaises(ValueError):
            Limits.parse_size('invalid')
        with self.assertRaises(ValueError):
            Limits.parse_size('1XB')

    def test_format_size(self):
        """Test formatting bytes into human-readable strings."""
        self.assertEqual(Limits.format_size(0), "unlimited")
        self.assertEqual(Limits.format_size(512), "512.0B")
        self.assertEqual(Limits.format_size(1024), "1.0KB")
        self.assertEqual(Limits.format_size(1024 * 1024), "1.0MB")
        self.assertEqual(Limits.format_size(1024 * 1024 * 1024), "1.0GB")

    def test_default_limits(self):
        """Test default limit values."""
        limits = Limits()
        self.assertEqual(limits.max_file_size, 1_048_576)  # 1MB
        self.assertEqual(limits.max_recursion, 8)
        self.assertEqual(limits.max_embeds_per_file, 100)
        self.assertEqual(limits.max_output_size, 10_485_760)  # 10MB
        self.assertEqual(limits.max_embed_text, 2_048)  # 2KB


class TestDiscovery(unittest.TestCase):
    """Test file and embed discovery."""

    def setUp(self):
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_discover_single_file(self):
        """Test discovering a single markdown file."""
        test_file = os.path.join(self.temp_dir, 'test.md')
        with open(test_file, 'w') as f:
            f.write('# Test')

        files = discover_files(test_file)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], os.path.abspath(test_file))

    def test_discover_directory(self):
        """Test discovering markdown files in a directory."""
        # Create test files
        for i in range(3):
            with open(os.path.join(self.temp_dir, f'test{i}.md'), 'w') as f:
                f.write(f'# Test {i}')

        # Create non-markdown file (should be ignored)
        with open(os.path.join(self.temp_dir, 'test.txt'), 'w') as f:
            f.write('Not markdown')

        files = discover_files(self.temp_dir)
        self.assertEqual(len(files), 3)

    def test_discover_embeds_in_file(self):
        """Test discovering embed directives in a file."""
        test_file = os.path.join(self.temp_dir, 'test.md')
        with open(test_file, 'w') as f:
            f.write("""# Test

```yaml
type: embed.file
source: example.txt
```

```yaml
type: embed.toc
```

Not an embed:
```python
print("hello")
```
""")

        embeds = discover_embeds_in_file(test_file)
        self.assertEqual(len(embeds), 2)
        self.assertEqual(embeds[0].embed_type, 'file')
        self.assertEqual(embeds[0].properties['source'], 'example.txt')
        self.assertEqual(embeds[1].embed_type, 'toc')

    def test_build_dependency_graph(self):
        """Test building dependency graph from embeds."""
        file1 = os.path.join(self.temp_dir, 'file1.md')
        file2 = os.path.join(self.temp_dir, 'file2.md')

        embeds = [
            EmbedDirective(
                file_path=file1,
                line_number=1,
                embed_type='file',
                properties={'source': 'file2.md'},
                source_file=file2
            )
        ]

        graph = build_dependency_graph(embeds)
        self.assertIn(file1, graph)
        self.assertIn(file2, graph[file1])

    def test_detect_cycles_simple(self):
        """Test detecting simple circular dependencies."""
        file1 = os.path.join(self.temp_dir, 'a.md')
        file2 = os.path.join(self.temp_dir, 'b.md')

        # a -> b -> a
        graph = {
            file1: {file2},
            file2: {file1}
        }

        cycles = detect_cycles(graph)
        self.assertGreater(len(cycles), 0)

    def test_detect_cycles_self_reference(self):
        """Test detecting self-referencing files."""
        file1 = os.path.join(self.temp_dir, 'loop.md')

        # file -> file
        graph = {
            file1: {file1}
        }

        cycles = detect_cycles(graph)
        self.assertGreater(len(cycles), 0)

    def test_calculate_max_depth(self):
        """Test calculating maximum dependency depth."""
        file1 = os.path.join(self.temp_dir, 'a.md')
        file2 = os.path.join(self.temp_dir, 'b.md')
        file3 = os.path.join(self.temp_dir, 'c.md')

        # a -> b -> c (depth 3)
        graph = {
            file1: {file2},
            file2: {file3},
            file3: set()
        }

        depth = calculate_max_depth(graph)
        self.assertEqual(depth, 3)


class TestValidation(unittest.TestCase):
    """Test validation phase."""

    def setUp(self):
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_validate_missing_file(self):
        """Test validation catches missing source files."""
        test_file = os.path.join(self.temp_dir, 'test.md')
        with open(test_file, 'w') as f:
            f.write("""```yaml
type: embed.file
source: missing.txt
```""")

        limits = Limits()
        result = validate_all(test_file, limits)

        self.assertTrue(result.has_errors())
        self.assertGreater(len(result.errors), 0)

    def test_validate_file_size_limit(self):
        """Test validation catches files exceeding size limit."""
        # Create a file larger than limit
        large_file = os.path.join(self.temp_dir, 'large.md')
        with open(large_file, 'w') as f:
            f.write('x' * 2000)  # 2KB

        # Set very small limit
        limits = Limits(max_file_size=100)
        result = validate_all(large_file, limits)

        self.assertTrue(result.has_errors())

    def test_validate_embed_count_limit(self):
        """Test validation catches too many embeds per file."""
        test_file = os.path.join(self.temp_dir, 'test.md')

        # Create file with 5 embeds
        with open(test_file, 'w') as f:
            for i in range(5):
                f.write(f"""```yaml
type: embed.toc
```

""")

        # Set limit to 3
        limits = Limits(max_embeds_per_file=3)
        result = validate_all(test_file, limits)

        self.assertTrue(result.has_errors())

    def test_validate_circular_dependency(self):
        """Test validation detects circular dependencies."""
        file1 = os.path.join(self.temp_dir, 'a.md')
        file2 = os.path.join(self.temp_dir, 'b.md')

        # Create circular dependency: a -> b -> a
        with open(file1, 'w') as f:
            f.write("""```yaml
type: embed.file
source: b.md
```""")

        with open(file2, 'w') as f:
            f.write("""```yaml
type: embed.file
source: a.md
```""")

        limits = Limits()
        # Validate the directory to discover both files
        result = validate_all(self.temp_dir, limits)

        self.assertTrue(result.has_errors())
        # Check for circular dependency error
        has_cycle_error = any(
            err.error_type == 'circular_dependency'
            for err in result.errors
        )
        self.assertTrue(has_cycle_error)

    def test_validate_success(self):
        """Test validation passes with valid files."""
        source_file = os.path.join(self.temp_dir, 'source.txt')
        test_file = os.path.join(self.temp_dir, 'test.md')

        with open(source_file, 'w') as f:
            f.write('Hello world')

        with open(test_file, 'w') as f:
            f.write("""```yaml
type: embed.file
source: source.txt
```""")

        limits = Limits()
        result = validate_all(test_file, limits)

        self.assertFalse(result.has_errors())


class TestProcessingContext(unittest.TestCase):
    """Test ProcessingContext for limit tracking."""

    def test_context_without_limits(self):
        """Test context without limits (unlimited mode)."""
        context = ProcessingContext(limits=None)

        # Should not return warnings
        for i in range(200):
            warning = context.increment_embed_count('/fake/file.md')
            self.assertIsNone(warning)

    def test_context_with_embed_limit(self):
        """Test context enforces embed count limit."""
        limits = Limits(max_embeds_per_file=3)
        context = ProcessingContext(limits=limits)

        file_path = '/fake/file.md'

        # First 3 should be fine
        for i in range(3):
            warning = context.increment_embed_count(file_path)
            self.assertIsNone(warning)

        # 4th should trigger warning
        warning = context.increment_embed_count(file_path)
        self.assertIsNotNone(warning)
        self.assertIn('Embed Limit Exceeded', warning)

    def test_context_tracks_per_file(self):
        """Test context tracks embeds separately per file."""
        limits = Limits(max_embeds_per_file=2)
        context = ProcessingContext(limits=limits)

        file1 = '/fake/file1.md'
        file2 = '/fake/file2.md'

        # Each file can have up to limit
        self.assertIsNone(context.increment_embed_count(file1))
        self.assertIsNone(context.increment_embed_count(file1))
        self.assertIsNone(context.increment_embed_count(file2))
        self.assertIsNone(context.increment_embed_count(file2))

        # Third for each file should warn
        self.assertIsNotNone(context.increment_embed_count(file1))
        self.assertIsNotNone(context.increment_embed_count(file2))


class TestForceMode(unittest.TestCase):
    """Test force mode with embedded warnings."""

    def setUp(self):
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_force_mode_missing_file(self):
        """Test force mode embeds warning for missing files."""
        test_file = os.path.join(self.temp_dir, 'test.md')
        with open(test_file, 'w') as f:
            f.write("""```yaml
type: embed.file
source: missing.txt
```""")

        # Process with limits (force mode simulation)
        context = ProcessingContext(limits=None)
        result = resolve_content(test_file, context=context)

        # Should contain warning in output
        self.assertIn('[!CAUTION]', result)
        self.assertIn('File not found', result)

    def test_force_mode_file_size_limit(self):
        """Test force mode embeds warning for file size limit."""
        large_file = os.path.join(self.temp_dir, 'large.txt')
        test_file = os.path.join(self.temp_dir, 'test.md')

        # Create large file
        with open(large_file, 'w') as f:
            f.write('x' * 1000)

        with open(test_file, 'w') as f:
            f.write("""```yaml
type: embed.file
source: large.txt
```""")

        # Process with very small limit
        limits = Limits(max_file_size=100)
        context = ProcessingContext(limits=limits)
        result = resolve_content(test_file, context=context)

        # Should contain warning in output
        self.assertIn('[!CAUTION]', result)
        self.assertIn('File Size Limit Exceeded', result)

    def test_force_mode_embed_count_limit(self):
        """Test force mode embeds warning when embed count exceeded."""
        test_file = os.path.join(self.temp_dir, 'test.md')

        # Create file with 3 TOC embeds
        with open(test_file, 'w') as f:
            f.write("""```yaml
type: embed.toc
```

```yaml
type: embed.toc
```

```yaml
type: embed.toc
```""")

        # Process with limit of 2
        limits = Limits(max_embeds_per_file=2)
        context = ProcessingContext(limits=limits)
        result = resolve_content(test_file, context=context)

        # Should contain warning in output
        self.assertIn('[!CAUTION]', result)
        self.assertIn('Embed Limit Exceeded', result)

    def test_force_mode_recursion_limit(self):
        """Test force mode embeds warning for recursion limit."""
        file1 = os.path.join(self.temp_dir, 'a.md')
        file2 = os.path.join(self.temp_dir, 'b.md')
        file3 = os.path.join(self.temp_dir, 'c.md')

        # Create chain: a -> b -> c
        with open(file1, 'w') as f:
            f.write("""```yaml
type: embed.file
source: b.md
```""")

        with open(file2, 'w') as f:
            f.write("""```yaml
type: embed.file
source: c.md
```""")

        with open(file3, 'w') as f:
            f.write('# End')

        # Process with recursion limit of 1
        limits = Limits(max_recursion=1)
        context = ProcessingContext(limits=limits)
        result = resolve_content(file1, context=context)

        # Should contain warning about recursion
        self.assertIn('[!CAUTION]', result)
        self.assertIn('Recursion Limit Exceeded', result)


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult model."""

    def test_has_errors(self):
        """Test has_errors method."""
        result = ValidationResult()
        self.assertFalse(result.has_errors())

        result.errors.append(ValidationError(
            file_path='test.md',
            line_number=1,
            error_type='test',
            message='Test error'
        ))
        self.assertTrue(result.has_errors())

    def test_format_report(self):
        """Test format_report method."""
        result = ValidationResult()
        result.files_to_process = ['a.md', 'b.md']
        result.embeds_discovered = [
            EmbedDirective('a.md', 1, 'file', {}, None),
            EmbedDirective('b.md', 1, 'toc', {}, None)
        ]

        report = result.format_report()
        self.assertIn('Validation Phase', report)
        self.assertIn('2 files', report)
        self.assertIn('2 embeds', report)

    def test_format_errors(self):
        """Test error formatting in report."""
        result = ValidationResult()
        result.errors.append(ValidationError(
            file_path='test.md',
            line_number=5,
            error_type='missing_file',
            message='File not found: example.txt'
        ))

        report = result.format_report()
        self.assertIn('Errors Found', report)
        self.assertIn('test.md:5', report)
        self.assertIn('File not found', report)


if __name__ == '__main__':
    unittest.main()
