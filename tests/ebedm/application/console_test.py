from unittest.mock import patch

from embedm.application.console import ContinueChoice, present_warnings, prompt_continue
from embedm.domain.status_level import Status, StatusLevel


def test_yes_returns_yes():
    with patch("builtins.input", return_value="y"):
        assert prompt_continue() == ContinueChoice.YES


def test_yes_full_word_returns_yes():
    with patch("builtins.input", return_value="yes"):
        assert prompt_continue() == ContinueChoice.YES


def test_always_returns_always():
    with patch("builtins.input", return_value="a"):
        assert prompt_continue() == ContinueChoice.ALWAYS


def test_always_full_word_returns_always():
    with patch("builtins.input", return_value="always"):
        assert prompt_continue() == ContinueChoice.ALWAYS


def test_no_returns_no():
    with patch("builtins.input", return_value="n"):
        assert prompt_continue() == ContinueChoice.NO


def test_empty_returns_no():
    with patch("builtins.input", return_value=""):
        assert prompt_continue() == ContinueChoice.NO


def test_unrecognised_returns_no():
    with patch("builtins.input", return_value="maybe"):
        assert prompt_continue() == ContinueChoice.NO


def test_x_returns_exit():
    with patch("builtins.input", return_value="x"):
        assert prompt_continue() == ContinueChoice.EXIT


def test_exit_full_word_returns_exit():
    with patch("builtins.input", return_value="exit"):
        assert prompt_continue() == ContinueChoice.EXIT


def test_keyboard_interrupt_returns_exit():
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        assert prompt_continue() == ContinueChoice.EXIT


def test_eof_returns_exit():
    with patch("builtins.input", side_effect=EOFError):
        assert prompt_continue() == ContinueChoice.EXIT


# --- present_warnings ---


def test_present_warnings_prints_to_stderr(capsys) -> None:
    warnings = [Status(StatusLevel.WARNING, "something went wrong")]

    present_warnings(warnings)

    captured = capsys.readouterr()
    assert "warning: something went wrong" in captured.err
    assert captured.out == ""


def test_present_warnings_multiple(capsys) -> None:
    warnings = [
        Status(StatusLevel.WARNING, "first warning"),
        Status(StatusLevel.WARNING, "second warning"),
    ]

    present_warnings(warnings)

    captured = capsys.readouterr()
    assert "warning: first warning" in captured.err
    assert "warning: second warning" in captured.err


def test_present_warnings_empty_list_prints_nothing(capsys) -> None:
    present_warnings([])

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""
