from unittest.mock import patch

from embedm.application.console import ContinueChoice, prompt_continue


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
