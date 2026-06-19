from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import AuthUser, UserRole
from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.services.category_service import CategoryService


@pytest.mark.asyncio
async def test_product_update_and_soft_delete(db_session) -> None:
    category = await CategoryService(db_session).create(CategoryCreate(name="UpdateCat"))
    await db_session.commit()
    creator = AuthUser(user_id=uuid4(), email="u@example.com", role=UserRole.ADMIN)
    service = ProductService(db_session)
    product = await service.create(
        ProductCreate(name="Desk Lamp", price=Decimal("25.00"), stock_quantity=4, category_id=category.id),
        creator,
    )
    await db_session.commit()

    updated = await service.update(
        product,
        ProductUpdate(
            name="Desk Lamp Pro",
            price=Decimal("30.00"),
            stock_quantity=6,
            category_id=category.id,
            is_active=True,
        ),
    )
    await db_session.commit()
    assert updated.slug == "desk-lamp-pro"

    deleted = await service.soft_delete(updated)
    await db_session.commit()
    assert deleted.is_active is False


@pytest.mark.asyncio
async def test_product_list_with_category_filter(db_session) -> None:
    category = await CategoryService(db_session).create(CategoryCreate(name="FilterMe"))
    await db_session.commit()
    creator = AuthUser(user_id=uuid4(), email="f@example.com", role=UserRole.ADMIN)
    service = ProductService(db_session)
    await service.create(
        ProductCreate(name="Filtered", price=Decimal("11.00"), stock_quantity=1, category_id=category.id),
        creator,
    )
    await db_session.commit()
    rows, total = await service.list_products(
        page=1,
        page_size=10,
        category_id=category.id,
        min_price=None,
        max_price=None,
        include_inactive=False,
    )
    assert total == 1
    assert rows[0].category_id == category.id
