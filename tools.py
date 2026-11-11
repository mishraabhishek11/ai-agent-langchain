from langchain_core.tools import tool


@tool
def current_time() -> str:
    """Return the current date and time."""
    from datetime import datetime

    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


@tool
def roll_dice() -> int:
    """Roll a six-sided dice."""
    import random

    return random.randint(1, 6)


@tool
def generate_password(length: int = 12) -> str:
    """Generate a random password."""

    import secrets
    import string

    characters = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*"
    )

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


