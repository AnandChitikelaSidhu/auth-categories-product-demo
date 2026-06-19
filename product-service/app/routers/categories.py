from math import ceil

from fastapi import APIRouter, Query, status

from app.dependencies.auth import AdminUser
from app.dependencies.deps import DbSession
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def _pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if total else 0


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> CategoryListResponse:
    service = CategoryService(db)
    rows, total = await service.list_categories(page, page_size)
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(row) for row in rows],
        total_count=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DbSession, _: AdminUser) -> CategoryResponse:
    category = await CategoryService(db).create(data)
    return CategoryResponse.model_validate(category)
