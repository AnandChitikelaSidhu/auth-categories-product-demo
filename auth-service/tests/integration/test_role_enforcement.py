import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_customer_cannot_access_admin_users_endpoint(
    client: AsyncClient,
    user_payload: dict[str, str],
) -> None:
    await client.post("/auth/register", json=user_payload)
    login_response = await client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    access_token = login_response.json()["access_token"]

    users_response = await client.get(
        "/auth/users",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert users_response.status_code == 403
    assert users_response.json()["detail"] == "Insufficient permissions"
