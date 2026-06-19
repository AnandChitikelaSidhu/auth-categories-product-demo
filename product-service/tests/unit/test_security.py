from uuid import uuid4

import pytest

from app.core.security import AuthUser, UserRole, is_admin_role, parse_auth_user, safe_decode_token
from tests.conftest import make_token


def test_parse_auth_user_from_payload() -> None:
    user_id = uuid4()
    payload = {
        "sub": str(user_id),
        "email": "user@example.com",
        "role": "admin",
        "type": "access",
    }
    user = parse_auth_user(payload)
    assert user.user_id == user_id
    assert user.role == UserRole.ADMIN


def test_is_admin_role_hierarchy() -> None:
    assert is_admin_role(UserRole.CUSTOMER) is False
    assert is_admin_role(UserRole.ADMIN) is True
    assert is_admin_role(UserRole.SUPER_ADMIN) is True


def test_safe_decode_token_round_trip() -> None:
    token = make_token("customer")
    user = safe_decode_token(token)
    assert user.role == UserRole.CUSTOMER
