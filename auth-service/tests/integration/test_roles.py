import pytest
from httpx import AsyncClient
from sqlalchemy import text

import app.core.database as database


@pytest.mark.asyncio
async def test_customer_cannot_list_roles(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    await client.post("/auth/register", json=user_payload)
    login_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_super_admin_can_list_roles(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    await client.post("/auth/register", json=user_payload)

    async with database.engine.begin() as connection:
        await connection.execute(
            text(
                """
                UPDATE users
                SET role_id = (SELECT id FROM roles WHERE name = 'super_admin')
                WHERE email = :email
                """
            ),
            {"email": user_payload["email"]},
        )

    login_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/roles",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    roles = response.json()
    assert len(roles) == 3
    assert [role["name"] for role in roles] == ["customer", "admin", "super_admin"]
    assert [role["level"] for role in roles] == [0, 1, 2]
    assert all(role["id"] for role in roles)
