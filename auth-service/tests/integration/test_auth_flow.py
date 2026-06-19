import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_access_logout_refresh_rejected(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    register_response = await client.post("/auth/register", json=user_payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == user_payload["email"]

    logout_response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 200

    me_after_logout = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_after_logout.status_code == 401
    assert me_after_logout.json()["detail"] == "Token has been revoked"

    refresh_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401
