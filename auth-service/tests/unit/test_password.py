import pytest
from pydantic import ValidationError

from app.core.password import validate_password_strength
from app.core.security import hash_password, verify_password
from app.schemas.auth import UserCreate


def test_hash_password_produces_bcrypt_hash() -> None:
    hashed = hash_password("Password1")
    assert hashed.startswith("$2b$")


def test_verify_password_accepts_correct_password() -> None:
    password = "Password1"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("Password1")
    assert verify_password("WrongPassword1", hashed) is False


def test_validate_password_strength_accepts_valid_password() -> None:
    assert validate_password_strength("Password1") == "Password1"


@pytest.mark.parametrize(
    "password",
    [
        "short1A",
        "alllowercase1",
        "NoDigitsHere",
        "",
    ],
)
def test_validate_password_strength_rejects_weak_passwords(password: str) -> None:
    with pytest.raises(ValueError, match="Password must be at least 8 characters"):
        validate_password_strength(password)


def test_user_create_schema_enforces_password_policy() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email="user@example.com",
            password="weakpassword",
            full_name="Test User",
        )
