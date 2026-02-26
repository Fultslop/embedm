"""Tests for symbol_parser — covers C/C++, C#, Java, and Python extraction."""
import pytest

from embedm.parsing.symbol_parser import (
    CSHARP_CONFIG,
    C_CPP_CONFIG,
    JAVA_CONFIG,
    PYTHON_CONFIG,
    extract_symbol,
    get_language_config,
)

# ---------------------------------------------------------------------------
# get_language_config
# ---------------------------------------------------------------------------


def test_get_language_config_cs():
    assert get_language_config("foo.cs") is CSHARP_CONFIG


def test_get_language_config_cpp():
    assert get_language_config("foo.cpp") is C_CPP_CONFIG


def test_get_language_config_h():
    assert get_language_config("foo.h") is C_CPP_CONFIG


def test_get_language_config_java():
    assert get_language_config("foo.java") is JAVA_CONFIG


def test_get_language_config_py():
    assert get_language_config("foo.py") is PYTHON_CONFIG


def test_get_language_config_unsupported():
    assert get_language_config("foo.go") is None
    assert get_language_config("foo.txt") is None


# ---------------------------------------------------------------------------
# C# extraction
# ---------------------------------------------------------------------------

_CS_CLASS = """\
public class MyService
{
    public void Start() { }
    public void Stop() { }
}
"""

_CS_METHOD = """\
public class Calc
{
    public int Add(int a, int b)
    {
        return a + b;
    }

    public int Sub(int a, int b)
    {
        return a - b;
    }
}
"""

_CS_OVERLOAD = """\
public class Parser
{
    public string Parse(string input)
    {
        return input;
    }

    public string Parse(string input, int flags)
    {
        return input;
    }
}
"""

_CS_INTERFACE = """\
public interface IRunner
{
    void Run();
}
"""

_CS_ENUM = """\
public enum Status
{
    Active,
    Inactive,
}
"""

_CS_NAMESPACE = """\
namespace MyApp
{
    public class Core
    {
        public void Init() { }
    }
}
"""

_CS_FILE_SCOPED_NS = """\
namespace MyApp;

public class Core
{
    public void Init() { }
}
"""


def test_cs_extract_class():
    lines = extract_symbol(_CS_CLASS, "MyService", CSHARP_CONFIG)
    assert lines is not None
    assert any("class MyService" in l for l in lines)
    assert lines[-1].strip() == "}"


def test_cs_extract_method():
    lines = extract_symbol(_CS_METHOD, "Add", CSHARP_CONFIG)
    assert lines is not None
    assert any("Add" in l for l in lines)
    assert any("return a + b" in l for l in lines)


def test_cs_extract_method_by_signature():
    lines = extract_symbol(_CS_OVERLOAD, "Parse(string, int)", CSHARP_CONFIG)
    assert lines is not None
    assert any("flags" in l for l in lines)


def test_cs_extract_method_empty_signature():
    lines = extract_symbol(_CS_OVERLOAD, "Parse(string)", CSHARP_CONFIG)
    assert lines is not None
    assert not any("flags" in l for l in lines)


def test_cs_extract_interface():
    lines = extract_symbol(_CS_INTERFACE, "IRunner", CSHARP_CONFIG)
    assert lines is not None
    assert any("interface IRunner" in l for l in lines)


def test_cs_extract_enum():
    lines = extract_symbol(_CS_ENUM, "Status", CSHARP_CONFIG)
    assert lines is not None
    assert any("enum Status" in l for l in lines)
    assert any("Active" in l for l in lines)


def test_cs_dot_notation_namespace_class():
    lines = extract_symbol(_CS_NAMESPACE, "MyApp.Core", CSHARP_CONFIG)
    assert lines is not None
    assert any("class Core" in l for l in lines)


def test_cs_dot_notation_namespace_method():
    lines = extract_symbol(_CS_NAMESPACE, "MyApp.Core.Init", CSHARP_CONFIG)
    assert lines is not None
    assert any("Init" in l for l in lines)


def test_cs_file_scoped_namespace():
    lines = extract_symbol(_CS_FILE_SCOPED_NS, "MyApp.Core", CSHARP_CONFIG)
    assert lines is not None
    assert any("class Core" in l for l in lines)


def test_cs_symbol_not_found():
    assert extract_symbol(_CS_CLASS, "NonExistent", CSHARP_CONFIG) is None


def test_cs_brace_in_string_ignored():
    source = """\
public class Safe
{
    public string GetBrace() { return "{not a block}"; }
    public void Real() { }
}
"""
    lines = extract_symbol(source, "Safe", CSHARP_CONFIG)
    assert lines is not None
    assert lines[-1].strip() == "}"


# ---------------------------------------------------------------------------
# C/C++ extraction
# ---------------------------------------------------------------------------

_CPP_SOURCE = """\
namespace Graphics
{
    class Renderer
    {
    public:
        void Draw(int x, int y);
        void Clear();
    };

    void Renderer::Draw(int x, int y)
    {
        // draw
    }
}
"""

_C_STRUCT = """\
struct Point
{
    int x;
    int y;
};
"""

_C_ENUM = """\
enum Color
{
    Red,
    Green,
    Blue,
};
"""


def test_cpp_extract_class():
    lines = extract_symbol(_CPP_SOURCE, "Renderer", C_CPP_CONFIG)
    assert lines is not None
    assert any("class Renderer" in l for l in lines)


def test_cpp_extract_namespace_class():
    lines = extract_symbol(_CPP_SOURCE, "Graphics.Renderer", C_CPP_CONFIG)
    assert lines is not None
    assert any("class Renderer" in l for l in lines)


def test_c_extract_struct():
    lines = extract_symbol(_C_STRUCT, "Point", C_CPP_CONFIG)
    assert lines is not None
    assert any("struct Point" in l for l in lines)
    assert any("int x" in l for l in lines)


def test_c_extract_enum():
    lines = extract_symbol(_C_ENUM, "Color", C_CPP_CONFIG)
    assert lines is not None
    assert any("enum Color" in l for l in lines)
    assert any("Green" in l for l in lines)


def test_cpp_not_found():
    assert extract_symbol(_CPP_SOURCE, "Missing", C_CPP_CONFIG) is None


# ---------------------------------------------------------------------------
# Java extraction
# ---------------------------------------------------------------------------

_JAVA_SOURCE = """\
public class Animal
{
    public void speak()
    {
        System.out.println("...");
    }
}

public class Dog extends Animal
{
    @Override
    public void speak()
    {
        System.out.println("Woof");
    }

    public void fetch(String item)
    {
        System.out.println("Fetching " + item);
    }
}
"""

_JAVA_INTERFACE = """\
public interface Runnable
{
    void run();
}
"""

_JAVA_ENUM = """\
public enum Day
{
    MON, TUE, WED;
}
"""


def test_java_extract_class():
    lines = extract_symbol(_JAVA_SOURCE, "Dog", JAVA_CONFIG)
    assert lines is not None
    assert any("class Dog" in l for l in lines)


def test_java_extract_method():
    lines = extract_symbol(_JAVA_SOURCE, "Dog.fetch", JAVA_CONFIG)
    assert lines is not None
    assert any("fetch" in l for l in lines)
    assert any("Fetching" in l for l in lines)


def test_java_extract_interface():
    lines = extract_symbol(_JAVA_INTERFACE, "Runnable", JAVA_CONFIG)
    assert lines is not None
    assert any("interface Runnable" in l for l in lines)


def test_java_extract_enum():
    lines = extract_symbol(_JAVA_ENUM, "Day", JAVA_CONFIG)
    assert lines is not None
    assert any("enum Day" in l for l in lines)


def test_java_not_found():
    assert extract_symbol(_JAVA_SOURCE, "Cat", JAVA_CONFIG) is None


# ---------------------------------------------------------------------------
# Regression: inner class with same name as outer class (Hello.cs scenario)
# ---------------------------------------------------------------------------

_CS_INNER_CLASS = """\
namespace test
{
    public class Example
    {
        public class Example
        {
            public void doSomething()
            {
                // inner Example of do something
            }
        }

        public void doSomething()
        {
            // base version
        }

        public void doSomething(string overloaded)
        {
            // overloaded version
        }

        public void doSomething(string overloaded, int extra)
        {
            // extra overloaded version
        }

        public void doSomethingElse()
        {
            // ...
        }
    }

    public class AnotherExample
    {
        public void doSomething()
        {
            // base version in another example
        }
    }
}
"""


def test_cs_inner_class_outer_method_resolved():
    """Example.doSomething() must resolve to the outer class's method, not the inner class's."""
    lines = extract_symbol(_CS_INNER_CLASS, "Example.doSomething()", CSHARP_CONFIG)
    assert lines is not None
    assert any("base version" in l for l in lines)
    assert not any("inner Example" in l for l in lines)


def test_cs_inner_class_inner_method_resolved():
    """Example.Example.doSomething() must resolve to the inner class's method."""
    lines = extract_symbol(_CS_INNER_CLASS, "Example.Example.doSomething()", CSHARP_CONFIG)
    assert lines is not None
    assert any("inner Example" in l for l in lines)


def test_cs_inner_class_overload_resolved():
    """Example.doSomething(string) must resolve to the overloaded outer method."""
    lines = extract_symbol(_CS_INNER_CLASS, "Example.doSomething(string)", CSHARP_CONFIG)
    assert lines is not None
    assert any("overloaded version" in l for l in lines)
    assert not any("extra overloaded" in l for l in lines)


def test_cs_inner_class_extra_overload_resolved():
    """Example.doSomething(string, int) must resolve to the extra overloaded outer method."""
    lines = extract_symbol(_CS_INNER_CLASS, "Example.doSomething(string, int)", CSHARP_CONFIG)
    assert lines is not None
    assert any("extra overloaded" in l for l in lines)


def test_cs_another_class_method_resolved():
    """AnotherExample.doSomething() must resolve to AnotherExample's method."""
    lines = extract_symbol(_CS_INNER_CLASS, "AnotherExample.doSomething()", CSHARP_CONFIG)
    assert lines is not None
    assert any("another example" in l for l in lines)


# ---------------------------------------------------------------------------
# Comment handling
# ---------------------------------------------------------------------------

_CS_BLOCK_COMMENT = """\
namespace foo {
    class Bar {
        /*
          public void doSomething()
          {
              // inside block comment
          }
        */

        public void doSomething()
        {
            // real
        }
    }
}
"""

_CS_LINE_COMMENT = """\
namespace foo {
    class Bar {
        // public void doSomething() { }

        public void doSomething()
        {
            // real
        }
    }
}
"""


def test_cs_symbol_inside_block_comment_is_skipped():
    """Symbol declared inside /* */ must be ignored; the real declaration is used."""
    lines = extract_symbol(_CS_BLOCK_COMMENT, "doSomething()", CSHARP_CONFIG)
    assert lines is not None
    assert any("// real" in l for l in lines)
    assert not any("inside block comment" in l for l in lines)


def test_cs_symbol_inside_line_comment_is_skipped():
    """Symbol declared after // must be ignored; the real declaration is used."""
    lines = extract_symbol(_CS_LINE_COMMENT, "doSomething()", CSHARP_CONFIG)
    assert lines is not None
    assert any("// real" in l for l in lines)


# ---------------------------------------------------------------------------
# Python extraction
# ---------------------------------------------------------------------------

_PY_CLASSES = """\
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return "Woof"

    def fetch(self, item: str) -> None:
        print(f"Fetching {item}")
"""

_PY_FUNCTIONS = """\
def add(x: int, y: int) -> int:
    return x + y


def subtract(x: int, y: int) -> int:
    return x - y
"""

_PY_ENUM = """\
from enum import Enum


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
"""

_PY_ASYNC = """\
class Service:
    async def fetch(self, url: str) -> str:
        return url
"""

_PY_COMMENT = """\
class Foo:
    # def fake(self): pass

    def real(self) -> None:
        pass
"""


def test_py_extract_class():
    lines = extract_symbol(_PY_CLASSES, "Animal", PYTHON_CONFIG)
    assert lines is not None
    assert any("class Animal" in l for l in lines)
    assert any("speak" in l for l in lines)


def test_py_extract_second_class():
    lines = extract_symbol(_PY_CLASSES, "Dog", PYTHON_CONFIG)
    assert lines is not None
    assert any("class Dog" in l for l in lines)
    assert any("fetch" in l for l in lines)
    assert not any("class Animal" in l for l in lines)


def test_py_dot_notation_class_method():
    lines = extract_symbol(_PY_CLASSES, "Dog.fetch", PYTHON_CONFIG)
    assert lines is not None
    assert any("def fetch" in l for l in lines)
    assert any("Fetching" in l for l in lines)


def test_py_dot_notation_excludes_other_class_method():
    """Dog.speak must resolve to Dog's method, not Animal's."""
    lines = extract_symbol(_PY_CLASSES, "Dog.speak", PYTHON_CONFIG)
    assert lines is not None
    assert any("Woof" in l for l in lines)
    assert not any('"..."' in l for l in lines)


def test_py_extract_function():
    lines = extract_symbol(_PY_FUNCTIONS, "add", PYTHON_CONFIG)
    assert lines is not None
    assert any("def add" in l for l in lines)
    assert any("return x + y" in l for l in lines)
    assert not any("subtract" in l for l in lines)


def test_py_extract_second_function():
    lines = extract_symbol(_PY_FUNCTIONS, "subtract", PYTHON_CONFIG)
    assert lines is not None
    assert any("def subtract" in l for l in lines)
    assert any("return x - y" in l for l in lines)


def test_py_extract_enum():
    lines = extract_symbol(_PY_ENUM, "Color", PYTHON_CONFIG)
    assert lines is not None
    assert any("class Color" in l for l in lines)
    assert any("RED" in l for l in lines)
    assert any("BLUE" in l for l in lines)


def test_py_extract_async_method():
    lines = extract_symbol(_PY_ASYNC, "Service.fetch", PYTHON_CONFIG)
    assert lines is not None
    assert any("async def fetch" in l for l in lines)


def test_py_symbol_inside_comment_is_skipped():
    """Symbol declared after # must be ignored; the real declaration is used."""
    lines = extract_symbol(_PY_COMMENT, "Foo.real", PYTHON_CONFIG)
    assert lines is not None
    assert any("def real" in l for l in lines)
    assert not any("fake" in l for l in lines)


def test_py_not_found():
    assert extract_symbol(_PY_CLASSES, "Cat", PYTHON_CONFIG) is None
