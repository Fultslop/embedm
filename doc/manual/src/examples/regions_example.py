"""Example file with named regions."""


def helper_function():
    """This is a helper function."""
    return "helper"


# md.start: main_function
def main_function(name):
    """
    The main function that we want to embed.

    This section is marked with md.start:main_function
    and md.end:main_function markers.
    """
    result = helper_function()
    print(f"Hello, {name}! Result: {result}")
    return result
# md.end: main_function


def another_function():
    """This function is not in the main_function region."""
    pass


if __name__ == "__main__":
    main_function("World")
