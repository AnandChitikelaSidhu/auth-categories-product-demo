import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_reports_database_and_redis(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert body["database"] in {"ok", "error"}
    assert body["redis"] in {"ok", "error"}
