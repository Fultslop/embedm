"""Tests for symbol extraction module."""

import pytest
from embedm.symbols import (
    extract_symbol,
    get_language_config,
    scan_line,
    ScanState,
    CommentStyle,
    extract_block_brace,
    extract_block_paren,
    extract_block_indent,
    extract_block_keyword,
)


# =============================================================================
# Test fixtures: sample source code
# =============================================================================

PYTHON_SAMPLE = """\
import os

def helper():
    return 42

class MyClass:
    \"\"\"A sample class.\"\"\"

    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    async def fetch_data(self):
        await something()
        return self.value

def standalone():
    x = 1
    y = 2
    return x + y
"""

PYTHON_DECORATED = """\
import os

@property
def name(self):
    return self._name

@staticmethod
@some_decorator(arg=True)
def decorated_func():
    pass

class Plain:
    pass
"""

JS_SAMPLE = """\
import { useState } from 'react';

function greet(name) {
    console.log("Hello, " + name);
}

export class Counter {
    constructor(initial) {
        this.count = initial;
    }

    increment() {
        this.count++;
    }
}

export async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}

const add = (a, b) => {
    return a + b;
};
"""

C_SAMPLE = """\
#include <stdio.h>

struct Point {
    int x;
    int y;
};

int add(int a, int b) {
    return a + b;
}

void print_point(struct Point p) {
    printf("(%d, %d)\\n", p.x, p.y);
}
"""

JAVA_SAMPLE = """\
package com.example;

public class Calculator {
    private int value;

    public Calculator(int initial) {
        this.value = initial;
    }

    public int add(int x) {
        return this.value + x;
    }

    private static int helper(int a, int b) {
        return a + b;
    }
}

public interface Printable {
    void print();
}
"""

CSHARP_SAMPLE = """\
using System;

public class Service {
    private readonly int _count;

    public Service(int count) {
        _count = count;
    }

    public int GetCount() {
        return _count;
    }

    public virtual async Task<string> FetchAsync() {
        return await Task.FromResult("data");
    }
}

public interface IService {
    int GetCount();
}
"""

SQL_SAMPLE = """\
-- Sample SQL with CTEs
WITH active_users AS (
    SELECT id, name
    FROM users
    WHERE active = 1
),
recent_orders AS (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    WHERE created_at > '2024-01-01'
    GROUP BY user_id
)
SELECT u.name, o.order_count
FROM active_users u
JOIN recent_orders o ON u.id = o.user_id;
"""

SQL_PROCEDURE = """\
CREATE OR REPLACE PROCEDURE update_stats(p_date DATE)
AS
BEGIN
    DELETE FROM stats WHERE stat_date = p_date;

    INSERT INTO stats (stat_date, total)
    SELECT p_date, COUNT(*) FROM events WHERE event_date = p_date;

    IF SQL%ROWCOUNT = 0 THEN
        BEGIN
            INSERT INTO stats (stat_date, total) VALUES (p_date, 0);
        END;
    END IF;
END;
"""


# =============================================================================
# State Machine Tests
# =============================================================================

class TestScanLine:
    """Test the string/comment state machine."""

    def _collect_chars(self, line, comment_style, state=None):
        """Helper: collect all real code characters from a line."""
        if state is None:
            state = ScanState()
        chars = []
        scan_line(line, state, comment_style, lambda c, p: chars.append(c))
        return ''.join(chars), state

    def test_plain_code(self):
        cs = CommentStyle(line_comment="#")
        result, _ = self._collect_chars("x = 1 + 2", cs)
        assert result == "x = 1 + 2"

    def test_skip_line_comment_hash(self):
        cs = CommentStyle(line_comment="#")
        result, _ = self._collect_chars("x = 1  # comment", cs)
        assert result == "x = 1  "

    def test_skip_line_comment_slashes(self):
        cs = CommentStyle(line_comment="//")
        result, _ = self._collect_chars("x = 1; // comment", cs)
        assert result == "x = 1; "

    def test_skip_block_comment(self):
        cs = CommentStyle(block_comment_start="/*", block_comment_end="*/")
        result, _ = self._collect_chars("x = /* hidden */ 1;", cs)
        assert result == "x =  1;"

    def test_block_comment_spans_lines(self):
        cs = CommentStyle(block_comment_start="/*", block_comment_end="*/")
        state = ScanState()
        r1, state = self._collect_chars("x = /* start", cs, state)
        assert state.in_block_comment is True
        r2, state = self._collect_chars("still comment */ y = 2;", cs, state)
        assert state.in_block_comment is False
        assert r2 == " y = 2;"

    def test_skip_double_quoted_string(self):
        cs = CommentStyle(line_comment="#")
        result, _ = self._collect_chars('x = "hello {}" + y', cs)
        assert '{' not in result
        assert 'hello' not in result

    def test_skip_single_quoted_string(self):
        cs = CommentStyle(line_comment="#")
        result, _ = self._collect_chars("x = '{braces}' + y", cs)
        assert '{' not in result

    def test_escaped_quote_not_string_end(self):
        cs = CommentStyle(line_comment="#")
        result, _ = self._collect_chars(r'x = "hello \" world" + y', cs)
        assert 'hello' not in result
        assert 'world' not in result

    def test_python_triple_quote(self):
        cs = CommentStyle(line_comment="#", triple_quote=True)
        result, _ = self._collect_chars('x = """triple""" + y', cs)
        assert 'triple' not in result
        assert '+ y' in result

    def test_triple_quote_spans_lines(self):
        cs = CommentStyle(line_comment="#", triple_quote=True)
        state = ScanState()
        r1, state = self._collect_chars('x = """start', cs, state)
        assert state.in_triple_quote is True
        r2, state = self._collect_chars('middle line', cs, state)
        assert r2 == ""
        r3, state = self._collect_chars('end""" + y', cs, state)
        assert state.in_triple_quote is False
        assert '+ y' in r3

    def test_sql_line_comment(self):
        cs = CommentStyle(line_comment="--", string_delimiters=["'"])
        result, _ = self._collect_chars("SELECT * -- from users", cs)
        assert result == "SELECT * "


# =============================================================================
# Block Extraction Strategy Tests
# =============================================================================

class TestBraceExtraction:
    """Test brace-delimited block extraction."""

    cs = CommentStyle(line_comment="//", block_comment_start="/*", block_comment_end="*/")

    def test_simple_function(self):
        lines = ["void foo() {", "    return;", "}"]
        assert extract_block_brace(lines, 0, self.cs) == 2

    def test_nested_braces(self):
        lines = [
            "void foo() {",
            "    if (x) {",
            "        bar();",
            "    }",
            "}",
        ]
        assert extract_block_brace(lines, 0, self.cs) == 4

    def test_brace_in_string_ignored(self):
        lines = [
            'void foo() {',
            '    printf("{");',
            '    printf("}");',
            '}',
        ]
        assert extract_block_brace(lines, 0, self.cs) == 3

    def test_brace_in_comment_ignored(self):
        lines = [
            "void foo() {",
            "    // }",
            "    return;",
            "}",
        ]
        assert extract_block_brace(lines, 0, self.cs) == 3

    def test_opening_brace_next_line(self):
        lines = [
            "void foo()",
            "{",
            "    return;",
            "}",
        ]
        assert extract_block_brace(lines, 0, self.cs) == 3

    def test_no_matching_brace_raises(self):
        lines = ["void foo() {", "    return;"]
        with pytest.raises(ValueError, match="No matching closing brace"):
            extract_block_brace(lines, 0, self.cs)


class TestParenExtraction:
    """Test parenthesis-delimited block extraction."""

    cs = CommentStyle(line_comment="--", string_delimiters=["'"])

    def test_simple_cte(self):
        lines = [
            "active_users AS (",
            "    SELECT id, name",
            "    FROM users",
            ")",
        ]
        assert extract_block_paren(lines, 0, self.cs) == 3

    def test_nested_parens(self):
        lines = [
            "stats AS (",
            "    SELECT COUNT(*)",
            "    FROM (SELECT * FROM t)",
            ")",
        ]
        assert extract_block_paren(lines, 0, self.cs) == 3

    def test_paren_in_string_ignored(self):
        lines = [
            "cte AS (",
            "    SELECT '(' as bracket",
            ")",
        ]
        assert extract_block_paren(lines, 0, self.cs) == 2


class TestIndentExtraction:
    """Test indentation-delimited block extraction."""

    cs = CommentStyle(line_comment="#", triple_quote=True)

    def test_simple_function(self):
        lines = [
            "def foo():",
            "    return 42",
            "",
            "def bar():",
        ]
        assert extract_block_indent(lines, 0, self.cs) == 1

    def test_function_with_blank_lines(self):
        lines = [
            "def foo():",
            "    x = 1",
            "",
            "    return x",
            "",
            "def bar():",
        ]
        assert extract_block_indent(lines, 0, self.cs) == 3

    def test_class_with_methods(self):
        lines = [
            "class Foo:",
            "    def a(self):",
            "        pass",
            "",
            "    def b(self):",
            "        pass",
            "",
            "x = 1",
        ]
        assert extract_block_indent(lines, 0, self.cs) == 5

    def test_nested_function(self):
        lines = [
            "    def inner():",
            "        return 1",
            "",
            "    def other():",
        ]
        assert extract_block_indent(lines, 0, self.cs) == 1

    def test_end_of_file(self):
        lines = [
            "def foo():",
            "    return 42",
        ]
        assert extract_block_indent(lines, 0, self.cs) == 1


class TestKeywordExtraction:
    """Test keyword-delimited block extraction."""

    cs = CommentStyle(line_comment="--", string_delimiters=["'"])

    def test_simple_begin_end(self):
        lines = [
            "CREATE PROCEDURE foo",
            "AS",
            "BEGIN",
            "    INSERT INTO t VALUES (1);",
            "END;",
        ]
        assert extract_block_keyword(lines, 0, self.cs) == 4

    def test_nested_begin_end(self):
        lines = [
            "CREATE PROCEDURE foo",
            "AS",
            "BEGIN",
            "    IF x THEN",
            "        BEGIN",
            "            INSERT INTO t VALUES (1);",
            "        END;",
            "    END IF;",
            "END;",
        ]
        assert extract_block_keyword(lines, 0, self.cs) == 8


# =============================================================================
# extract_symbol() Tests — Python
# =============================================================================

class TestExtractSymbolPython:
    """Test symbol extraction from Python source."""

    def test_extract_function(self):
        result = extract_symbol(PYTHON_SAMPLE, "helper", "test.py")
        assert result is not None
        assert result['lines'][0].strip() == "def helper():"
        assert "return 42" in result['lines'][1]

    def test_extract_class(self):
        result = extract_symbol(PYTHON_SAMPLE, "MyClass", "test.py")
        assert result is not None
        assert result['lines'][0].strip() == "class MyClass:"
        # Should include all methods
        joined = '\n'.join(result['lines'])
        assert "get_value" in joined
        assert "fetch_data" in joined

    def test_extract_method_dot_notation(self):
        result = extract_symbol(PYTHON_SAMPLE, "MyClass.get_value", "test.py")
        assert result is not None
        assert "def get_value" in result['lines'][0]
        assert "return self.value" in result['lines'][1]

    def test_extract_async_method(self):
        result = extract_symbol(PYTHON_SAMPLE, "MyClass.fetch_data", "test.py")
        assert result is not None
        assert "async def fetch_data" in result['lines'][0]

    def test_extract_standalone_function(self):
        result = extract_symbol(PYTHON_SAMPLE, "standalone", "test.py")
        assert result is not None
        assert "def standalone():" in result['lines'][0]
        joined = '\n'.join(result['lines'])
        assert "x = 1" in joined
        assert "return x + y" in joined

    def test_startLine_correct(self):
        result = extract_symbol(PYTHON_SAMPLE, "helper", "test.py")
        assert result is not None
        # helper is on line 3 (1-indexed)
        assert result['startLine'] == 3

    def test_symbol_not_found(self):
        result = extract_symbol(PYTHON_SAMPLE, "nonexistent", "test.py")
        assert result is None

    def test_decorator_included(self):
        result = extract_symbol(PYTHON_DECORATED, "name", "test.py")
        assert result is not None
        assert result['lines'][0].strip() == "@property"
        assert "def name" in result['lines'][1]

    def test_multiple_decorators_included(self):
        result = extract_symbol(PYTHON_DECORATED, "decorated_func", "test.py")
        assert result is not None
        assert result['lines'][0].strip() == "@staticmethod"
        assert "@some_decorator" in result['lines'][1]
        assert "def decorated_func" in result['lines'][2]


# =============================================================================
# extract_symbol() Tests — JavaScript/TypeScript
# =============================================================================

class TestExtractSymbolJS:
    """Test symbol extraction from JavaScript source."""

    def test_extract_function(self):
        result = extract_symbol(JS_SAMPLE, "greet", "test.js")
        assert result is not None
        assert "function greet" in result['lines'][0]
        joined = '\n'.join(result['lines'])
        assert "console.log" in joined

    def test_extract_class(self):
        result = extract_symbol(JS_SAMPLE, "Counter", "test.js")
        assert result is not None
        assert "class Counter" in result['lines'][0]
        joined = '\n'.join(result['lines'])
        assert "constructor" in joined
        assert "increment" in joined

    def test_extract_async_function(self):
        result = extract_symbol(JS_SAMPLE, "fetchData", "test.js")
        assert result is not None
        assert "async function fetchData" in result['lines'][0]

    def test_extract_const(self):
        result = extract_symbol(JS_SAMPLE, "add", "test.js")
        assert result is not None
        assert "const add" in result['lines'][0]

    def test_typescript_extension(self):
        result = extract_symbol(JS_SAMPLE, "greet", "test.ts")
        assert result is not None

    def test_tsx_extension(self):
        result = extract_symbol(JS_SAMPLE, "greet", "test.tsx")
        assert result is not None


# =============================================================================
# extract_symbol() Tests — C/C++
# =============================================================================

class TestExtractSymbolC:
    """Test symbol extraction from C/C++ source."""

    def test_extract_struct(self):
        result = extract_symbol(C_SAMPLE, "Point", "test.c")
        assert result is not None
        assert "struct Point" in result['lines'][0]
        joined = '\n'.join(result['lines'])
        assert "int x" in joined
        assert "int y" in joined

    def test_extract_function(self):
        result = extract_symbol(C_SAMPLE, "add", "test.c")
        assert result is not None
        assert "int add" in result['lines'][0]
        assert "return a + b" in '\n'.join(result['lines'])

    def test_cpp_extension(self):
        result = extract_symbol(C_SAMPLE, "add", "test.cpp")
        assert result is not None


# =============================================================================
# extract_symbol() Tests — Java
# =============================================================================

class TestExtractSymbolJava:
    """Test symbol extraction from Java source."""

    def test_extract_class(self):
        result = extract_symbol(JAVA_SAMPLE, "Calculator", "test.java")
        assert result is not None
        assert "class Calculator" in result['lines'][0]
        joined = '\n'.join(result['lines'])
        assert "add" in joined
        assert "helper" in joined

    def test_extract_interface(self):
        result = extract_symbol(JAVA_SAMPLE, "Printable", "test.java")
        assert result is not None
        assert "interface Printable" in result['lines'][0]

    def test_extract_method_dot_notation(self):
        result = extract_symbol(JAVA_SAMPLE, "Calculator.add", "test.java")
        assert result is not None
        assert "int add" in result['lines'][0]


# =============================================================================
# extract_symbol() Tests — C#
# =============================================================================

class TestExtractSymbolCSharp:
    """Test symbol extraction from C# source."""

    def test_extract_class(self):
        result = extract_symbol(CSHARP_SAMPLE, "Service", "test.cs")
        assert result is not None
        assert "class Service" in result['lines'][0]

    def test_extract_interface(self):
        result = extract_symbol(CSHARP_SAMPLE, "IService", "test.cs")
        assert result is not None
        assert "interface IService" in result['lines'][0]

    def test_extract_method(self):
        result = extract_symbol(CSHARP_SAMPLE, "Service.GetCount", "test.cs")
        assert result is not None
        assert "GetCount" in result['lines'][0]

    def test_extract_async_method(self):
        result = extract_symbol(CSHARP_SAMPLE, "Service.FetchAsync", "test.cs")
        assert result is not None
        assert "FetchAsync" in result['lines'][0]


# =============================================================================
# extract_symbol() Tests — SQL
# =============================================================================

class TestExtractSymbolSQL:
    """Test symbol extraction from SQL source."""

    def test_extract_first_cte(self):
        result = extract_symbol(SQL_SAMPLE, "active_users", "test.sql")
        assert result is not None
        joined = '\n'.join(result['lines'])
        assert "active_users AS" in joined
        assert "SELECT id, name" in joined

    def test_extract_second_cte(self):
        result = extract_symbol(SQL_SAMPLE, "recent_orders", "test.sql")
        assert result is not None
        joined = '\n'.join(result['lines'])
        assert "recent_orders AS" in joined
        assert "order_count" in joined

    def test_extract_procedure(self):
        result = extract_symbol(SQL_PROCEDURE, "update_stats", "test.sql")
        assert result is not None
        joined = '\n'.join(result['lines'])
        assert "CREATE OR REPLACE PROCEDURE" in joined
        assert "DELETE FROM stats" in joined


# =============================================================================
# get_language_config() Tests
# =============================================================================

class TestGetLanguageConfig:
    """Test language config lookup."""

    def test_python(self):
        config = get_language_config("test.py")
        assert config is not None
        assert config.name == "Python"

    def test_javascript(self):
        config = get_language_config("test.js")
        assert config is not None
        assert config.name == "JavaScript/TypeScript"

    def test_typescript(self):
        config = get_language_config("test.ts")
        assert config is not None

    def test_c(self):
        config = get_language_config("test.c")
        assert config is not None
        assert config.name == "C/C++"

    def test_java(self):
        config = get_language_config("test.java")
        assert config is not None

    def test_csharp(self):
        config = get_language_config("test.cs")
        assert config is not None

    def test_sql(self):
        config = get_language_config("test.sql")
        assert config is not None

    def test_unknown_extension(self):
        config = get_language_config("test.xyz")
        assert config is None

    def test_markdown_not_supported(self):
        config = get_language_config("test.md")
        assert config is None


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_unknown_extension_returns_none(self):
        result = extract_symbol("def foo(): pass", "foo", "test.xyz")
        assert result is None

    def test_empty_content(self):
        result = extract_symbol("", "foo", "test.py")
        assert result is None

    def test_symbol_at_end_of_file(self):
        code = "def last():\n    return True"
        result = extract_symbol(code, "last", "test.py")
        assert result is not None
        assert "return True" in '\n'.join(result['lines'])

    def test_windows_line_endings(self):
        code = "def foo():\r\n    return 1\r\n\r\ndef bar():\r\n    return 2\r\n"
        result = extract_symbol(code, "foo", "test.py")
        assert result is not None
        assert "return 1" in '\n'.join(result['lines'])

    def test_first_match_wins(self):
        code = "def helper():\n    return 1\n\ndef helper():\n    return 2\n"
        result = extract_symbol(code, "helper", "test.py")
        assert result is not None
        assert "return 1" in '\n'.join(result['lines'])
