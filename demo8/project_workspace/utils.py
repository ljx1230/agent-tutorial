def greet_user(name: str) -> str:
    if not name:
        return "Hello!"
    return f"Hello, {name}!"
