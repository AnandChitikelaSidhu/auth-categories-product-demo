from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import AuthUser, is_admin_role, safe_decode_token

security_scheme = HTTPBearer(auto_error=False)


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden() -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _extract_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()
    return credentials.credentials


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> AuthUser | None:
    if credentials is None:
        return None
    try:
        return safe_decode_token(_extract_token(credentials))
    except ValueError as exc:
        raise _unauthorized(str(exc)) from exc


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> AuthUser:
    return safe_decode_token(_extract_token(credentials))


async def require_admin(
    user: Annotated[AuthUser, Depends(get_current_user)],
) -> AuthUser:
    if not is_admin_role(user.role):
        raise _forbidden()
    return user


OptionalUser = Annotated[AuthUser | None, Depends(get_optional_user)]
CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
AdminUser = Annotated[AuthUser, Depends(require_admin)]
