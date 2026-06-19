from math import ceil
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.slug import build_unique_slug, slugify_name
from app.models.category import Category
from app.schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, category_id: UUID) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        result = await self.db.execute(select(Category.id).where(Category.slug == slug))
        return result.scalar_one_or_none() is not None

    async def create(self, data: CategoryCreate) -> Category:
        base_slug = slugify_name(data.name)
        slug = await build_unique_slug(base_slug, self.slug_exists)
        category = Category(name=data.name, slug=slug)
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def list_categories(self, page: int, page_size: int) -> tuple[list[Category], int]:
        offset = (page - 1) * page_size
        total = int((await self.db.execute(select(func.count()).select_from(Category))).scalar_one())
        result = await self.db.execute(
            select(Category).order_by(Category.name).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    def pages(total: int, page_size: int) -> int:
        return ceil(total / page_size) if total else 0
