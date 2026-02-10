"""Sample Python file for symbol extraction regression tests."""


class Calculator:
    """A simple calculator class."""

    def __init__(self, value=0):
        self.value = value

    def add(self, x):
        self.value += x
        return self

    def result(self):
        return self.value


def standalone_helper(items):
    """A standalone function."""
    return [item * 2 for item in items]
