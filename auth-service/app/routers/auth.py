from math import ceil
from typing import Annotated
from uuid import UUID
from app.schemas.user_response import build_user_response
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies.auth import (
    AdminUser,
    CurrentUser,
    DbSession,
    RedisClient,
    SuperAdminUser,
    security_scheme,
)
from app.schemas.auth import (
    MessageResponse,
    PaginatedUsersResponse,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)
from app.services.rate_limit_service import RateLimitService
from app.services.token_service import TokenService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(data: UserCreate, db: DbSession) -> UserResponse:
    user_service = UserService(db)
    existing = await user_service.get_by_email(data.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = await user_service.create_user(data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: DbSession, redis: RedisClient) -> TokenResponse:
    rate_limiter = RateLimitService(redis)
    if await rate_limiter.is_login_locked(data.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again in 15 minutes.",
        )

    user_service = UserService(db)
    user = await user_service.authenticate(data.email, data.password)
    if user is None:
        await rate_limiter.record_failed_login(data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    await rate_limiter.clear_failed_logins(data.email)
    await user_service.update_last_login(user)
    token_service = TokenService(redis)
    return await token_service.issue_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: TokenRefresh,
    db: DbSession,
    redis: RedisClient,
) -> TokenResponse:
    token_service = TokenService(redis)
    user_service = UserService(db)

    try:
        user_id = await token_service.validate_refresh_token(data.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    try:
        return await token_service.rotate_refresh_token(data.refresh_token, user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: TokenRefresh,
    redis: RedisClient,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    _: CurrentUser,
) -> MessageResponse:
    token_service = TokenService(redis)
    try:
        await token_service.blacklist_refresh_token(data.refresh_token)
        if credentials is not None:
            await token_service.blacklist_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser,db: DbSession) -> UserResponse:
    #return UserResponse.model_validate(current_user)
    user_service = UserService(db)
    user_permissions = await user_service.get_permissions(current_user)
    return build_user_response(current_user, permissions=user_permissions)



@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> UserResponse:
    user_service = UserService(db)
    user = await user_service.update_full_name(current_user, data)
    return UserResponse.model_validate(user)


@router.get("/users", response_model=PaginatedUsersResponse)
async def list_users(
    _: AdminUser,
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedUsersResponse:
    user_service = UserService(db)
    users, total = await user_service.list_users(page=page, page_size=page_size)
    return PaginatedUsersResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total > 0 else 0,
    )


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    _: SuperAdminUser,
    db: DbSession,
) -> UserResponse:
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    updated_user = await user_service.update_role(user, data.role)
    return UserResponse.model_validate(updated_user)
