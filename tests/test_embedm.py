import unittest
import tempfile
import os
import shutil
from pathlib import Path

# Assuming the main script is named mdembed.py
# Import all functions we want to test
from mdembed import (
    parse_embed_options,
    extract_region,
    extract_lines,
    format_with_line_numbers_text,
    format_with_line_numbers,
    dedent_lines,
    csv_to_markdown_table,
    slugify,
    generate_table_of_contents,
    resolve_content,
    resolve_table_of_contents
)


class TestParseEmbedOptions(unittest.TestCase):
    """Tests for parse_embed_options function"""
    
    def test_empty_content(self):
        result = parse_embed_options("")
        self.assertIsNone(result['title'])
        self.assertFalse(result['line_numbers'])
    
    def test_title_only(self):
        result = parse_embed_options("title: My Title")
        self.assertEqual(result['title'], "My Title")
        self.assertFalse(result['line_numbers'])
    
    def test_line_numbers_html(self):
        result = parse_embed_options("line_numbers: html")
        self.assertEqual(result['line_numbers'], 'html')
    
    def test_line_numbers_text(self):
        result = parse_embed_options("line_numbers: text")
        self.assertEqual(result['line_numbers'], 'text')
    
    def test_line_numbers_true(self):
        result = parse_embed_options("line_numbers: true")
        self.assertEqual(result['line_numbers'], 'html')  # Defaults to html
    
    def test_line_numbers_false(self):
        result = parse_embed_options("line_numbers: false")
        self.assertFalse(result['line_numbers'])
    
    def test_both_options(self):
        result = parse_embed_options("title: Test Title\nline_numbers: text")
        self.assertEqual(result['title'], "Test Title")
        self.assertEqual(result['line_numbers'], 'text')


class TestExtractRegion(unittest.TestCase):
    """Tests for extract_region function"""
    
    def test_valid_region(self):
        content = """line 1
line 2
# md.start:myregion
line 4
line 5
# md.end:myregion
line 7"""
        result = extract_region(content, "myregion")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 4', 'line 5'])
        self.assertEqual(result['startLine'], 4)
    
    def test_region_with_whitespace(self):
        content = """line 1
// md.start: myregion
line 3
// md.end: myregion
line 5"""
        result = extract_region(content, "myregion")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 3'])
    
    def test_nonexistent_region(self):
        content = "line 1\nline 2\nline 3"
        result = extract_region(content, "missing")
        self.assertIsNone(result)
    
    def test_missing_end_marker(self):
        content = "# md.start:test\nline 2\nline 3"
        result = extract_region(content, "test")
        self.assertIsNone(result)


class TestExtractLines(unittest.TestCase):
    """Tests for extract_lines function"""
    
    def test_single_line(self):
        content = "line 1\nline 2\nline 3\nline 4\nline 5"
        result = extract_lines(content, "L3")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 3'])
        self.assertEqual(result['startLine'], 3)
    
    def test_line_range(self):
        content = "line 1\nline 2\nline 3\nline 4\nline 5"
        result = extract_lines(content, "L2-4")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 2', 'line 3', 'line 4'])
        self.assertEqual(result['startLine'], 2)
    
    def test_line_range_with_l_prefix(self):
        content = "line 1\nline 2\nline 3\nline 4\nline 5"
        result = extract_lines(content, "L2-L4")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 2', 'line 3', 'line 4'])
    
    def test_line_to_end(self):
        content = "line 1\nline 2\nline 3\nline 4\nline 5"
        result = extract_lines(content, "L3-")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 3', 'line 4', 'line 5'])
    
    def test_invalid_format(self):
        content = "line 1\nline 2"
        result = extract_lines(content, "invalid")
        self.assertIsNone(result)
    
    def test_case_insensitive(self):
        content = "line 1\nline 2\nline 3"
        result = extract_lines(content, "l2")
        self.assertIsNotNone(result)
        self.assertEqual(result['lines'], ['line 2'])


class TestFormatWithLineNumbersText(unittest.TestCase):
    """Tests for format_with_line_numbers_text function"""
    
    def test_basic_formatting(self):
        lines = ['def hello():', '    print("world")']
        result = format_with_line_numbers_text(lines, 1)
        self.assertIn('1 | def hello():', result)
        self.assertIn('2 |     print("world")', result)
    
    def test_removes_common_indent(self):
        lines = ['    def hello():', '        print("world")']
        result = format_with_line_numbers_text(lines, 1)
        self.assertIn('1 | def hello():', result)
        self.assertIn('2 |     print("world")', result)
    
    def test_line_number_padding(self):
        lines = ['line'] * 100
        result = format_with_line_numbers_text(lines, 1)
        lines_result = result.split('\n')
        # First line should have padding
        self.assertTrue(lines_result[0].startswith('  1 |'))
        # Line 100 should not have extra padding
        self.assertTrue(lines_result[99].startswith('100 |'))
    
    def test_empty_lines(self):
        result = format_with_line_numbers_text([], 1)
        self.assertEqual(result, "")
    
    def test_custom_start_line(self):
        lines = ['code line 1', 'code line 2']
        result = format_with_line_numbers_text(lines, 42)
        self.assertIn('42 |', result)
        self.assertIn('43 |', result)


class TestDedentLines(unittest.TestCase):
    """Tests for dedent_lines function"""
    
    def test_removes_common_indent(self):
        lines = ['    line 1', '    line 2', '        line 3']
        result = dedent_lines(lines)
        self.assertEqual(result, 'line 1\nline 2\n    line 3')
    
    def test_empty_list(self):
        result = dedent_lines([])
        self.assertEqual(result, "")
    
    def test_no_indent(self):
        lines = ['line 1', 'line 2']
        result = dedent_lines(lines)
        self.assertEqual(result, 'line 1\nline 2')
    
    def test_mixed_empty_lines(self):
        lines = ['    line 1', '', '    line 3']
        result = dedent_lines(lines)
        self.assertEqual(result, 'line 1\n\nline 3')


class TestCsvToMarkdownTable(unittest.TestCase):
    """Tests for csv_to_markdown_table function"""
    
    def test_basic_csv(self):
        csv = "Name,Age,City\nAlice,30,NYC\nBob,25,LA"
        result = csv_to_markdown_table(csv)
        self.assertIn('| Name | Age | City |', result)
        self.assertIn('| --- | --- | --- |', result)
        self.assertIn('| Alice | 30 | NYC |', result)
        self.assertIn('| Bob | 25 | LA |', result)
    
    def test_quoted_fields(self):
        csv = 'Name,Description\nAlice,"Hello, World"\nBob,"Test"'
        result = csv_to_markdown_table(csv)
        self.assertIn('| Alice | Hello, World |', result)
    
    def test_escaped_quotes(self):
        csv = 'Name,Quote\nAlice,"""Hello"""'
        result = csv_to_markdown_table(csv)
        self.assertIn('| Alice | "Hello" |', result)
    
    def test_empty_csv(self):
        result = csv_to_markdown_table("")
        self.assertEqual(result, '')
    
    def test_uneven_rows(self):
        csv = "A,B,C\n1,2\n3,4,5"
        result = csv_to_markdown_table(csv)
        # Should pad missing cells
        self.assertIn('| 1 | 2 |', result)


class TestSlugify(unittest.TestCase):
    """Tests for slugify function"""
    
    def test_basic_text(self):
        self.assertEqual(slugify("Hello World"), "hello-world")
    
    def test_special_characters(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")
    
    def test_multiple_spaces(self):
        self.assertEqual(slugify("Hello   World"), "hello-world")
    
    def test_underscores(self):
        self.assertEqual(slugify("Hello_World"), "hello-world")
    
    def test_leading_trailing_hyphens(self):
        self.assertEqual(slugify("-Hello World-"), "hello-world")
    
    def test_numbers(self):
        self.assertEqual(slugify("Version 2.0"), "version-20")
    
    def test_empty_string(self):
        self.assertEqual(slugify(""), "")


class TestGenerateTableOfContents(unittest.TestCase):
    """Tests for generate_table_of_contents function"""
    
    def test_basic_headings(self):
        content = "# Title\n## Subtitle\n### Section"
        result = generate_table_of_contents(content)
        self.assertIn('- [Title](#title)', result)
        self.assertIn('  - [Subtitle](#subtitle)', result)
        self.assertIn('    - [Section](#section)', result)
    
    def test_duplicate_headings(self):
        content = "# Introduction\n## Details\n# Introduction"
        result = generate_table_of_contents(content)
        self.assertIn('- [Introduction](#introduction)', result)
        self.assertIn('- [Introduction](#introduction-1)', result)
    
    def test_no_headings(self):
        content = "Just some text\nNo headings here"
        result = generate_table_of_contents(content)
        self.assertIn('No headings found', result)
    
    def test_heading_with_special_chars(self):
        content = "# Hello, World!"
        result = generate_table_of_contents(content)
        self.assertIn('[Hello, World!](#hello-world)', result)


class TestResolveContentIntegration(unittest.TestCase):
    """Integration tests for resolve_content function"""
    
    def setUp(self):
        """Create a temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def create_file(self, filename, content):
        """Helper to create test files"""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    def test_simple_embed(self):
        # Create source file
        code_path = self.create_file('code.py', 'def hello():\n    print("world")')
        
        # Create markdown with embed
        md_content = f'# Test\n\n```embed\nfile: code.py\n```'
        md_path = self.create_file('test.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('def hello():', result)
        self.assertIn('```py', result)
    
    def test_embed_with_line_range(self):
        code_path = self.create_file('code.py', 'line1\nline2\nline3\nline4\nline5')
        md_content = f'```embed\nfile: code.py#L2-4\n```'
        md_path = self.create_file('test.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('line2', result)
        self.assertIn('line3', result)
        self.assertIn('line4', result)
        self.assertNotIn('line1', result)
        self.assertNotIn('line5', result)
    
    def test_embed_with_title(self):
        code_path = self.create_file('code.py', 'print("test")')
        md_content = f'```embed\nfile: code.py\ntitle: My Code\n```'
        md_path = self.create_file('test.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('**My Code**', result)
    
    def test_csv_embed(self):
        csv_path = self.create_file('data.csv', 'Name,Age\nAlice,30\nBob,25')
        md_content = f'```embed\nfile: data.csv\n```'
        md_path = self.create_file('test.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('| Name | Age |', result)
        self.assertIn('| Alice | 30 |', result)
    
    def test_recursive_markdown_embed(self):
        # Create nested markdown file
        nested_path = self.create_file('nested.md', '## Nested Section\n\nSome content')
        
        # Create main markdown that embeds it
        md_content = f'# Main\n\n```embed\nfile: nested.md\n```'
        md_path = self.create_file('main.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('## Nested Section', result)
        self.assertIn('Some content', result)
    
    def test_file_not_found(self):
        md_content = '```embed\nfile: nonexistent.py\n```'
        md_path = self.create_file('test.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('File not found', result)
        self.assertIn('nonexistent.py', result)
    
    def test_infinite_loop_detection(self):
        # Create file that tries to embed itself
        md_content = '# Test\n\n```embed\nfile: self.md\n```'
        md_path = self.create_file('self.md', md_content)
        
        result = resolve_content(md_path)
        self.assertIn('Infinite loop detected', result)


class TestResolveTableOfContents(unittest.TestCase):
    """Tests for resolve_table_of_contents function"""
    
    def test_toc_generation(self):
        content = """# Main Title
````embed
table_of_contents
````

## Section 1
## Section 2"""
        
        result = resolve_table_of_contents(content)
        self.assertIn('- [Main Title](#main-title)', result)
        self.assertIn('  - [Section 1](#section-1)', result)
        self.assertIn('  - [Section 2](#section-2)', result)
        # Should not contain the embed marker
        self.assertNotIn('```embed', result)
    
    def test_multiple_toc_embeds(self):
        content = """# Title
````embed
table_of_contents
````

## Section
````embed
table_of_contents
```"""
        
        result = resolve_table_of_contents(content)
        # Both embeds should be replaced with the same TOC
        toc_count = result.count('- [Title](#title)')
        self.assertEqual(toc_count, 2)


class TestFormatWithLineNumbersHTML(unittest.TestCase):
    """Tests for format_with_line_numbers (HTML) function"""
    
    def test_html_generation(self):
        lines = ['def hello():', '    print("world")']
        result = format_with_line_numbers(lines, 1, 'python')
        
        self.assertIn('<div class="code-block-with-lines">', result)
        self.assertIn('<style>', result)
        self.assertIn('class="line-number"', result)
        self.assertIn('language-python', result)
    
    def test_html_escaping(self):
        lines = ['if x < 5 && y > 3:', '    print("test")']
        result = format_with_line_numbers(lines, 1, 'python')
        
        self.assertIn('&lt;', result)  # < should be escaped
        self.assertIn('&amp;&amp;', result)  # && should be escaped
    
    def test_empty_lines_html(self):
        result = format_with_line_numbers([], 1, 'python')
        self.assertEqual(result, "")


if __name__ == '__main__':
    # Run all tests with verbose output
    unittest.main(verbosity=2)
