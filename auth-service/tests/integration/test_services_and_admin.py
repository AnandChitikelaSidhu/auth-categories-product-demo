import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.database as database
from app.core.security import decode_token
from app.models.user import UserRole
from app.schemas.auth import UserCreate, UserUpdate
from app.services.rate_limit_service import RateLimitService
from app.services.token_service import TokenService
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_user_service_create_and_authenticate(db_session: AsyncSession) -> None:
    service = UserService(db_session)
    user = await service.create_user(
        UserCreate(email="svc@example.com", password="Password1", full_name="Svc User")
    )
    await db_session.commit()

    assert user.email == "svc@example.com"
    assert user.role == UserRole.CUSTOMER

    authenticated = await service.authenticate("svc@example.com", "Password1")
    assert authenticated is not None
    assert authenticated.id == user.id

    missing = await service.authenticate("svc@example.com", "WrongPassword1")
    assert missing is None


@pytest.mark.asyncio
async def test_user_service_update_full_name_and_list_users(db_session: AsyncSession) -> None:
    service = UserService(db_session)
    user = await service.create_user(
        UserCreate(email="list@example.com", password="Password1", full_name="List User")
    )
    await db_session.commit()

    updated = await service.update_full_name(user, UserUpdate(full_name="Updated Name"))
    await db_session.commit()
    assert updated.full_name == "Updated Name"

    users, total = await service.list_users(page=1, page_size=10)
    assert total >= 1
    assert any(item.email == "list@example.com" for item in users)


@pytest.mark.asyncio
async def test_user_service_update_role(db_session: AsyncSession) -> None:
    service = UserService(db_session)
    user = await service.create_user(
        UserCreate(email="role@example.com", password="Password1", full_name="Role User")
    )
    await db_session.commit()

    promoted = await service.update_role(user, UserRole.ADMIN)
    await db_session.commit()
    assert promoted.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_token_service_issue_validate_and_blacklist(
    db_session: AsyncSession,
    redis_client,
) -> None:
    service = UserService(db_session)
    user = await service.create_user(
        UserCreate(email="token@example.com", password="Password1", full_name="Token User")
    )
    await db_session.commit()

    token_service = TokenService(redis_client)
    tokens = await token_service.issue_tokens(user)
    user_id = await token_service.validate_refresh_token(tokens.refresh_token)
    assert user_id == user.id

    await token_service.blacklist_refresh_token(tokens.refresh_token)

    with pytest.raises(ValueError, match="revoked"):
        await token_service.validate_refresh_token(tokens.refresh_token)

    await token_service.blacklist_access_token(tokens.access_token)

    payload = decode_token(tokens.access_token)
    assert await token_service.is_access_token_revoked(payload["jti"]) is True


@pytest.mark.asyncio
async def test_rate_limit_service_locks_after_max_attempts(redis_client) -> None:
    service = RateLimitService(redis_client)
    email = "ratelimit@example.com"

    assert await service.is_login_locked(email) is False

    for _ in range(5):
        await service.record_failed_login(email)

    assert await service.is_login_locked(email) is True

    await service.clear_failed_logins(email)
    assert await service.is_login_locked(email) is False


@pytest.mark.asyncio
async def test_admin_can_list_users_and_super_admin_can_update_role(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    register_response = await client.post("/auth/register", json=user_payload)
    user_id = register_response.json()["id"]

    async with database.engine.begin() as connection:
        await connection.execute(
            text("UPDATE users SET role = 'super_admin' WHERE email = :email"),
            {"email": user_payload["email"]},
        )

    login_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    users_response = await client.get("/auth/users", headers=headers)
    assert users_response.status_code == 200
    body = users_response.json()
    assert body["total"] >= 1
    assert len(body["items"]) >= 1

    role_response = await client.patch(
        f"/auth/users/{user_id}/role",
        headers=headers,
        json={"role": "admin"},
    )
    assert role_response.status_code == 200
    assert role_response.json()["role"] == "admin"

    patch_me_response = await client.patch(
        "/auth/me",
        headers=headers,
        json={"full_name": "Updated Admin"},
    )
    assert patch_me_response.status_code == 200
    assert patch_me_response.json()["full_name"] == "Updated Admin"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    first = await client.post("/auth/register", json=user_payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=user_payload)
    assert second.status_code == 409
