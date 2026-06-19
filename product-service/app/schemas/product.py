from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_validator


class ProductCreate(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: Decimal = Field(ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    category_id: UUID
    is_active: bool = True

    @field_validator("price", mode="before")
    @classmethod
    def coerce_price(cls, value: object) -> Decimal:
        return Decimal(str(value))

    @field_validator("category_id", mode="before")
    @classmethod
    def coerce_category_id(cls, value: object) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))


class ProductUpdate(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: Decimal = Field(ge=0)
    stock_quantity: int = Field(ge=0)
    category_id: UUID
    is_active: bool = True

    @field_validator("price", mode="before")
    @classmethod
    def coerce_price(cls, value: object) -> Decimal:
        return Decimal(str(value))

    @field_validator("category_id", mode="before")
    @classmethod
    def coerce_category_id(cls, value: object) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))


class StockDelta(BaseModel):
    model_config = ConfigDict(strict=True)

    delta: int


class CategoryBrief(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    name: str
    slug: str


class ProductResponse(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    price: Decimal
    stock_quantity: int
    category_id: UUID
    category: CategoryBrief | None = None
    is_active: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[ProductResponse]
    total_count: int
    page: int
    page_size: int
    pages: int


class HealthResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    status: str
    database: str
    redis: str
