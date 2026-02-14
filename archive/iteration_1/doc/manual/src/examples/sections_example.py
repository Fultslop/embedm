"""Example file for demonstrating line ranges."""


def function_one():
    """First function (lines 4-6)."""
    print("Function one")


def function_two():
    """Second function (lines 9-14)."""
    for i in range(3):
        print(f"Iteration {i}")
    return "done"


def function_three():
    """Third function (lines 17-22)."""
    data = {
        "key1": "value1",
        "key2": "value2"
    }
    return data


class ExampleClass:
    """Example class (lines 25-30)."""

    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello from {self.name}"
