import pytest
from httpx import AsyncClient


async def _seed_product(client: AsyncClient, admin_headers: dict[str, str]) -> tuple[dict, dict]:
    category = await client.post("/categories", json={"name": "Gadgets"}, headers=admin_headers)
    category_id = category.json()["id"]
    product = await client.post(
        "/products",
        json={
            "name": "Keyboard",
            "price": 49.99,
            "stock_quantity": 5,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    return category.json(), product.json()


@pytest.mark.asyncio
async def test_stock_delta_valid_and_invalid(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    _, product = await _seed_product(client, admin_headers)

    ok = await client.patch(
        f"/products/{product['id']}/stock",
        json={"delta": -2},
        headers=admin_headers,
    )
    assert ok.status_code == 200
    assert ok.json()["stock_quantity"] == 3

    bad = await client.patch(
        f"/products/{product['id']}/stock",
        json={"delta": -10},
        headers=admin_headers,
    )
    assert bad.status_code == 400
    assert "negative" in bad.json()["detail"].lower()


@pytest.mark.asyncio
async def test_multiple_stock_decrements(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    _, product = await _seed_product(client, admin_headers)

    for _ in range(5):
        response = await client.patch(
            f"/products/{product['id']}/stock",
            json={"delta": -1},
            headers=admin_headers,
        )
        assert response.status_code == 200

    final = await client.get(f"/products/{product['id']}")
    assert final.json()["stock_quantity"] == 0
