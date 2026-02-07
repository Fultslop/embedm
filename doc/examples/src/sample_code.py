def calculate_factorial(n):
    """Calculate factorial of n"""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def main():
    result = calculate_factorial(5)
    print(f"Factorial of 5 is {result}")

if __name__ == "__main__":
    main()
