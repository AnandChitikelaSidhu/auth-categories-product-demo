import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_post_product_unauthenticated_returns_401(client: AsyncClient) -> None:
    payload = {
        "name": "Phone",
        "price": 999.99,
        "stock_quantity": 1,
        "category_id": "00000000-0000-0000-0000-000000000001",
    }
    response = await client.post("/products", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_post_product_customer_returns_403(
    client: AsyncClient,
    customer_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Phone",
        "price": 999.99,
        "stock_quantity": 1,
        "category_id": "00000000-0000-0000-0000-000000000001",
    }
    response = await client.post("/products", json=payload, headers=customer_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_soft_delete_hides_from_public_list(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    category = await client.post("/categories", json={"name": "Books"}, headers=admin_headers)
    category_id = category.json()["id"]
    product = await client.post(
        "/products",
        json={"name": "Python Guide", "price": 19.99, "stock_quantity": 3, "category_id": category_id},
        headers=admin_headers,
    )
    product_id = product.json()["id"]

    deleted = await client.delete(f"/products/{product_id}", headers=admin_headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    public = await client.get("/products")
    assert all(item["id"] != product_id for item in public.json()["items"])

    admin_view = await client.get("/products?include_inactive=true", headers=admin_headers)
    assert any(item["id"] == product_id for item in admin_view.json()["items"])
