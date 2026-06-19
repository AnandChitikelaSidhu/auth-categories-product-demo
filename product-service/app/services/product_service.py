from decimal import Decimal
from math import ceil
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import noload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthUser
from app.core.slug import build_unique_slug, slugify_name
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, product_id: UUID) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_id_or_slug(self, identifier: str) -> Product | None:
        filters = [Product.slug == identifier]
        try:
            filters.append(Product.id == UUID(identifier))
        except ValueError:
            pass
        query = select(Product).where(or_(*filters))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        query = select(Product.id).where(Product.slug == slug)
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _resolve_slug(self, name: str, exclude_id: UUID | None = None) -> str:
        base = slugify_name(name)
        return await build_unique_slug(
            base,
            lambda candidate: self.slug_exists(candidate, exclude_id=exclude_id),
        )

    async def create(self, data: ProductCreate, creator: AuthUser) -> Product:
        slug = await self._resolve_slug(data.name)
        product = Product(
            name=data.name,
            slug=slug,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
            category_id=data.category_id,
            is_active=data.is_active,
            created_by=creator.user_id,
        )
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def update(self, product: Product, data: ProductUpdate) -> Product:
        if data.name != product.name:
            product.slug = await self._resolve_slug(data.name, exclude_id=product.id)
        product.name = data.name
        product.description = data.description
        product.price = data.price
        product.stock_quantity = data.stock_quantity
        product.category_id = data.category_id
        product.is_active = data.is_active
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def get_for_update(self, product_id: UUID) -> Product | None:
        query = (
            select(Product)
            .options(noload(Product.category))
            .where(Product.id == product_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def apply_stock_delta(self, product_id: UUID, delta: int) -> Product:
        locked = await self.get_for_update(product_id)
        if locked is None:
            raise ValueError("Product not found")
        new_stock = locked.stock_quantity + delta
        if new_stock < 0:
            raise ValueError("Stock quantity cannot be negative")
        locked.stock_quantity = new_stock
        await self.db.flush()
        await self.db.refresh(locked)
        return locked

    async def soft_delete(self, product: Product) -> Product:
        product.is_active = False
        await self.db.flush()
        await self.db.refresh(product)
        return product

    def to_response(self, product: Product) -> ProductResponse:
        return ProductResponse.model_validate(product)

    async def list_products(
        self,
        *,
        page: int,
        page_size: int,
        category_id: UUID | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        include_inactive: bool,
    ) -> tuple[list[Product], int]:
        filters = []
        if not include_inactive:
            filters.append(Product.is_active.is_(True))
        if category_id:
            filters.append(Product.category_id == category_id)
        if min_price is not None:
            filters.append(Product.price >= min_price)
        if max_price is not None:
            filters.append(Product.price <= max_price)
        where_clause = and_(*filters) if filters else True
        offset = (page - 1) * page_size
        total = int(
            (await self.db.execute(select(func.count()).select_from(Product).where(where_clause))).scalar_one()
        )
        result = await self.db.execute(
            select(Product).where(where_clause).order_by(Product.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    def pages(total: int, page_size: int) -> int:
        return ceil(total / page_size) if total else 0
