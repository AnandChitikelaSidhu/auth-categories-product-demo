import re

from pydantic import field_validator

PASSWORD_POLICY_MESSAGE = (
    "Password must be at least 8 characters with one uppercase letter and one number"
)


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not re.search(r"[A-Z]", password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not re.search(r"\d", password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    return password
