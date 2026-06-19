import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_products_with_filters(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    category = await client.post("/categories", json={"name": "FilterCat"}, headers=admin_headers)
    category_id = category.json()["id"]
    await client.post(
        "/products",
        json={"name": "Cheap Item", "price": 5.00, "stock_quantity": 1, "category_id": category_id},
        headers=admin_headers,
    )
    await client.post(
        "/products",
        json={"name": "Premium Item", "price": 50.00, "stock_quantity": 1, "category_id": category_id},
        headers=admin_headers,
    )

    filtered = await client.get("/products", params={"min_price": 10, "max_price": 100})
    assert filtered.status_code == 200
    names = [item["name"] for item in filtered.json()["items"]]
    assert "Premium Item" in names
    assert "Cheap Item" not in names


@pytest.mark.asyncio
async def test_inactive_product_hidden_from_public_get(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    category = await client.post("/categories", json={"name": "Hidden"}, headers=admin_headers)
    created = await client.post(
        "/products",
        json={"name": "Hidden Product", "price": 12.00, "stock_quantity": 1, "category_id": category.json()["id"]},
        headers=admin_headers,
    )
    product_id = created.json()["id"]
    await client.delete(f"/products/{product_id}", headers=admin_headers)

    public = await client.get(f"/products/{product_id}")
    assert public.status_code == 404

    admin = await client.get(f"/products/{product_id}", headers=admin_headers)
    assert admin.status_code == 200
