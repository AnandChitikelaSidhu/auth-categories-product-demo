from decimal import Decimal
from math import ceil
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.core.security import is_admin_role
from app.dependencies.auth import AdminUser, OptionalUser
from app.dependencies.deps import DbSession, RedisClient
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate, StockDelta
from app.services.cache_service import CACHE_HEADER, ProductCacheService
from app.services.category_service import CategoryService
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def _pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if total else 0


async def _require_category(db: DbSession, category_id: UUID) -> None:
    found = await CategoryService(db).get_by_id(category_id)
    if found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


async def _get_product(service: ProductService, identifier: str):
    product = await service.get_by_id_or_slug(identifier)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


async def _invalidate_cache(redis: RedisClient, product_id: UUID) -> None:
    await ProductCacheService(redis).invalidate(str(product_id))


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: DbSession,
    user: OptionalUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: UUID | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    include_inactive: bool = False,
) -> ProductListResponse:
    if include_inactive and (user is None or not is_admin_role(user.role)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    service = ProductService(db)
    rows, total = await service.list_products(
        page=page,
        page_size=page_size,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        include_inactive=include_inactive,
    )
    return ProductListResponse(
        items=[service.to_response(row) for row in rows],
        total_count=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


@router.get("/{identifier}", response_model=ProductResponse)
async def get_product(
    identifier: str,
    db: DbSession,
    redis: RedisClient,
    response: Response,
    user: OptionalUser,
) -> ProductResponse:
    service = ProductService(db)
    product = await _get_product(service, identifier)
    if not product.is_active and (user is None or not is_admin_role(user.role)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    cache = ProductCacheService(redis)
    cached = await cache.get_product(str(product.id))
    if cached is not None:
        response.headers[CACHE_HEADER] = "HIT"
        return cached

    payload = service.to_response(product)
    await cache.set_product(payload)
    response.headers[CACHE_HEADER] = "MISS"
    return payload


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, db: DbSession, admin: AdminUser) -> ProductResponse:
    await _require_category(db, data.category_id)
    service = ProductService(db)
    product = await service.create(data, admin)
    return service.to_response(product)


@router.put("/{identifier}", response_model=ProductResponse)
async def update_product(
    identifier: str,
    data: ProductUpdate,
    db: DbSession,
    redis: RedisClient,
    _: AdminUser,
) -> ProductResponse:
    await _require_category(db, data.category_id)
    service = ProductService(db)
    product = await _get_product(service, identifier)
    updated = await service.update(product, data)
    await _invalidate_cache(redis, updated.id)
    return service.to_response(updated)


@router.patch("/{identifier}/stock", response_model=ProductResponse)
async def patch_stock(
    identifier: str,
    data: StockDelta,
    db: DbSession,
    redis: RedisClient,
    _: AdminUser,
) -> ProductResponse:
    service = ProductService(db)
    product = await _get_product(service, identifier)
    try:
        updated = await service.apply_stock_delta(product.id, data.delta)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    await _invalidate_cache(redis, updated.id)
    return service.to_response(updated)


@router.delete("/{identifier}", response_model=ProductResponse)
async def delete_product(
    identifier: str,
    db: DbSession,
    redis: RedisClient,
    _: AdminUser,
) -> ProductResponse:
    service = ProductService(db)
    product = await _get_product(service, identifier)
    deleted = await service.soft_delete(product)
    await _invalidate_cache(redis, deleted.id)
    return service.to_response(deleted)
