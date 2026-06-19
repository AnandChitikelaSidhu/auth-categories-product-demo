import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refresh_token_rotation_rejects_old_token(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    await client.post("/auth/register", json=user_payload)
    login_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    old_refresh_token = login_response.json()["refresh_token"]

    refresh_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["refresh_token"] != old_refresh_token

    old_token_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert old_token_response.status_code == 401

    new_token_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert new_token_response.status_code == 200
