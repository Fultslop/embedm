"""Example Python module for symbol extraction."""


class Calculator:
    """A basic calculator."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b


class Formatter:
    """A text formatter."""

    def bold(self, text):
        """Wrap text in bold markers."""
        return f"**{text}**"


def standalone_helper(items):
    """A standalone utility function."""
    return [str(item) for item in items]
