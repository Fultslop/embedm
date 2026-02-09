# Table Line Numbers Test

This tests file embedding with table-formatted line numbers (GitHub-compatible).

## Full File with Table Line Numbers

| Line | Code |
|-----:|------|
| 1 | `"""Sample Python file for regression testing."""` |
| 2 |  |
| 3 |  |
| 4 | `def greet(name: str) -> str:` |
| 5 | `    """Greet someone by name.` |
| 6 |  |
| 7 | `    Args:` |
| 8 | `        name: Person's name` |
| 9 |  |
| 10 | `    Returns:` |
| 11 | `        Greeting message` |
| 12 | `    """` |
| 13 | `    return f"Hello, {name}!"` |
| 14 |  |
| 15 |  |
| 16 | `def calculate_sum(a: int, b: int) -> int:` |
| 17 | `    """Calculate sum of two numbers.` |
| 18 |  |
| 19 | `    Args:` |
| 20 | `        a: First number` |
| 21 | `        b: Second number` |
| 22 |  |
| 23 | `    Returns:` |
| 24 | `        Sum of a and b` |
| 25 | `    """` |
| 26 | `    return a + b` |
| 27 |  |
| 28 |  |
| 29 | `if __name__ == "__main__":` |
| 30 | `    print(greet("World"))` |
| 31 | `    print(f"Sum: {calculate_sum(10, 20)}")` |
| 32 |  |

## Specific Region with Table Line Numbers

| Line | Code |
|-----:|------|
| 1 | `"""Sample Python file for regression testing."""` |
| 2 |  |
| 3 |  |
| 4 | `def greet(name: str) -> str:` |
| 5 | `    """Greet someone by name.` |
| 6 |  |
| 7 | `    Args:` |
| 8 | `        name: Person's name` |
| 9 |  |
| 10 | `    Returns:` |
| 11 | `        Greeting message` |
| 12 | `    """` |
| 13 | `    return f"Hello, {name}!"` |
| 14 |  |
| 15 |  |
| 16 | `def calculate_sum(a: int, b: int) -> int:` |
| 17 | `    """Calculate sum of two numbers.` |
| 18 |  |
| 19 | `    Args:` |
| 20 | `        a: First number` |
| 21 | `        b: Second number` |
| 22 |  |
| 23 | `    Returns:` |
| 24 | `        Sum of a and b` |
| 25 | `    """` |
| 26 | `    return a + b` |
| 27 |  |
| 28 |  |
| 29 | `if __name__ == "__main__":` |
| 30 | `    print(greet("World"))` |
| 31 | `    print(f"Sum: {calculate_sum(10, 20)}")` |
| 32 |  |

## Table Format Benefits

The table format:
- ✅ Works natively on GitHub (no CSS required)
- ✅ Line numbers are visually separated from code
- ✅ Each line is in its own table row
- ✅ Code is formatted with inline backticks
- ❌ Cannot be copied as continuous code (table structure remains)
