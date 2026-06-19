import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category_requires_admin(client: AsyncClient, customer_headers: dict[str, str]) -> None:
    response = await client.post("/categories", json={"name": "Denied"}, headers=customer_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_put_and_delete_product(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    category = await client.post("/categories", json={"name": "Ops"}, headers=admin_headers)
    category_id = category.json()["id"]
    created = await client.post(
        "/products",
        json={"name": "Chair", "price": 99.00, "stock_quantity": 2, "category_id": category_id},
        headers=admin_headers,
    )
    product_id = created.json()["id"]

    updated = await client.put(
        f"/products/{product_id}",
        json={
            "name": "Office Chair",
            "price": 109.00,
            "stock_quantity": 3,
            "category_id": category_id,
            "is_active": True,
        },
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Office Chair"

    deleted = await client.delete(f"/products/{product_id}", headers=admin_headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False
