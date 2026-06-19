from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


ROLE_LEVELS: dict[UserRole, int] = {
    UserRole.CUSTOMER: 0,
    UserRole.ADMIN: 1,
    UserRole.SUPER_ADMIN: 2,
}


@dataclass(frozen=True, slots=True)
class AuthUser:
    user_id: UUID
    email: str
    role: UserRole


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def parse_auth_user(payload: dict[str, Any]) -> AuthUser:
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return AuthUser(
        user_id=UUID(payload["sub"]),
        email=payload["email"],
        role=UserRole(payload["role"]),
    )


def is_admin_role(role: UserRole) -> bool:
    return ROLE_LEVELS[role] >= ROLE_LEVELS[UserRole.ADMIN]


def safe_decode_token(token: str) -> AuthUser:
    try:
        return parse_auth_user(decode_access_token(token))
    except (JWTError, ValueError, KeyError) as exc:
        raise ValueError("Could not validate credentials") from exc
