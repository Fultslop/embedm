"""Sample Python file for regression testing."""


def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: Person's name

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


if __name__ == "__main__":
    print(greet("World"))
    print(f"Sum: {calculate_sum(10, 20)}")
