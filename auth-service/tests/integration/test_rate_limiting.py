import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sixth_failed_login_returns_429(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    await client.post("/auth/register", json=user_payload)

    for _ in range(5):
        response = await client.post(
            "/auth/login",
            json={"email": user_payload["email"], "password": "WrongPassword1"},
        )
        assert response.status_code == 401

    sixth_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": "WrongPassword1"},
    )
    assert sixth_response.status_code == 429
    assert "Too many failed login attempts" in sixth_response.json()["detail"]
