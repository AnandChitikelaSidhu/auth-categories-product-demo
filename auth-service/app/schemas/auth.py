from datetime import datetime
from math import ceil
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.password import validate_password_strength


class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def password_policy(cls, value: str) -> str:
        return validate_password_strength(value)


class UserLogin(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()


class UserUpdate(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    full_name: str = Field(min_length=1, max_length=100)


class UserRoleUpdate(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    role: str = Field(min_length=1, max_length=50)


class RoleResponse(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    level: int


class TokenRefresh(BaseModel):
    model_config = ConfigDict(strict=True)

    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    last_name: str | None = None
    role_id: UUID
    role: str
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None
    permissions: list[str] = []
    created_at: datetime
    updated_at: datetime


class PaginatedUsersResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MessageResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    message: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    status: str
    database: str
    redis: str
