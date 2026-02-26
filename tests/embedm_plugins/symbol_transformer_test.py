from embedm.parsing.symbol_parser import CSHARP_CONFIG
from embedm_plugins.file.symbol_transformer import SymbolParams, SymbolTransformer

_SOURCE = """\
public class Greeter
{
    public string Hello(string name)
    {
        return "Hello " + name;
    }
}
"""


def _run(content: str, symbol: str) -> str | None:
    return SymbolTransformer().execute(SymbolParams(content=content, symbol_name=symbol, config=CSHARP_CONFIG))


def test_extract_class():
    result = _run(_SOURCE, "Greeter")
    assert result is not None
    assert "class Greeter" in result


def test_extract_method():
    result = _run(_SOURCE, "Hello")
    assert result is not None
    assert "Hello" in result
    assert "return" in result


def test_not_found_returns_none():
    assert _run(_SOURCE, "Missing") is None
