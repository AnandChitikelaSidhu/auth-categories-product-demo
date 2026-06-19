from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.slug import slugify_name


class CategoryCreate(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    name: str
    slug: str
    created_at: datetime


class CategoryListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[CategoryResponse]
    total_count: int
    page: int
    page_size: int
    pages: int
