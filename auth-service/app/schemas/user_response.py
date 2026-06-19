from app.models.user import User
from app.schemas.auth import UserResponse


def build_user_response(user: User, *, permissions: list[str]) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        last_name=user.last_name,
        role_id=user.role_id,
        role=user.role.name,
        permissions=permissions,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
