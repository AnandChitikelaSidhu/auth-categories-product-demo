from uuid import uuid4

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    is_token_valid,
)

settings = get_settings()


def test_create_and_decode_access_token() -> None:
    user_id = uuid4()
    email = "user@example.com"
    role = "customer"
    jti = str(uuid4())

    token = create_access_token(subject=user_id, email=email, role=role, jti=jti)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["role"] == role
    assert payload["jti"] == jti
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_create_and_decode_refresh_token() -> None:
    user_id = uuid4()
    jti = str(uuid4())

    token = create_refresh_token(subject=user_id, jti=jti)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_is_token_valid_checks_token_type() -> None:
    assert is_token_valid({"type": "access"}, "access") is True
    assert is_token_valid({"type": "refresh"}, "access") is False
    assert is_token_valid({"type": "refresh"}, "refresh") is True


def test_decode_token_rejects_tampered_token() -> None:
    user_id = uuid4()
    token = create_access_token(
        subject=user_id,
        email="user@example.com",
        role="customer",
        jti=str(uuid4()),
    )
    tampered = f"{token}invalid"

    with pytest.raises(Exception):
        decode_token(tampered)


def test_access_token_uses_configured_algorithm() -> None:
    user_id = uuid4()
    token = create_access_token(
        subject=user_id,
        email="user@example.com",
        role="customer",
        jti=str(uuid4()),
    )
    header = jwt.get_unverified_header(token)
    assert header["alg"] == settings.jwt_algorithm
