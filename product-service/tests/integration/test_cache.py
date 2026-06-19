import asyncio

import pytest
from httpx import AsyncClient


async def _create_category(client: AsyncClient, headers: dict[str, str]) -> dict:
    response = await client.post("/categories", json={"name": "Electronics"}, headers=headers)
    assert response.status_code == 201
    return response.json()


async def _create_product(client: AsyncClient, headers: dict[str, str], category_id: str) -> dict:
    payload = {
        "name": "Wireless Mouse",
        "description": "Ergonomic mouse",
        "price": 29.99,
        "stock_quantity": 10,
        "category_id": category_id,
    }
    response = await client.post("/products", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_cache_miss_then_hit(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    category = await _create_category(client, admin_headers)
    product = await _create_product(client, admin_headers, category["id"])

    first = await client.get(f"/products/{product['id']}")
    assert first.status_code == 200
    assert first.headers["X-Cache"] == "MISS"

    second = await client.get(f"/products/{product['id']}")
    assert second.status_code == 200
    assert second.headers["X-Cache"] == "HIT"
    assert second.json()["id"] == product["id"]


@pytest.mark.asyncio
async def test_update_invalidates_cache(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    category = await _create_category(client, admin_headers)
    product = await _create_product(client, admin_headers, category["id"])
    await client.get(f"/products/{product['id']}")

    update_payload = {
        "name": "Wireless Mouse Pro",
        "description": "Updated",
        "price": 34.99,
        "stock_quantity": 12,
        "category_id": category["id"],
        "is_active": True,
    }
    updated = await client.put(f"/products/{product['id']}", json=update_payload, headers=admin_headers)
    assert updated.status_code == 200

    after = await client.get(f"/products/{product['id']}")
    assert after.headers["X-Cache"] == "MISS"
    assert after.json()["name"] == "Wireless Mouse Pro"
