def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    print(f"3 + 5 = {add(3, 5)}")
    print(f"3 * 5 = {multiply(3, 5)}")