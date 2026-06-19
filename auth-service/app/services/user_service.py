from datetime import UTC, datetime
from math import ceil
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password
from app.models.role import Permission, Role, role_permissions
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate
from app.services.role_service import RoleService


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_permissions(self, user: User) -> list[str]:
        result = await self.db.execute(
            select(Permission.code)
            .join(role_permissions, role_permissions.c.permission_id == Permission.id)
            .join(Role, Role.id == role_permissions.c.role_id)
            .where(Role.id == user.role_id)
            .order_by(Permission.code)
        )
        return list(result.scalars().all())

    async def create_user(self, data: UserCreate, *, role_name: str = "customer") -> User:
        role = await RoleService(self.db).get_by_name(role_name)
        if role is None:
            raise ValueError(f"Role not found: {role_name}")

        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            last_name=data.last_name,
            role_id=role.id,
        )
        self.db.add(user)
        await self.db.flush()
        user.role = role
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.get_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_last_login(self, user: User) -> User:
        user.last_login_at = datetime.now(UTC)
        await self.db.flush()
        return user

    async def update_full_name(self, user: User, data: UserUpdate) -> User:
        user.full_name = data.full_name
        await self.db.flush()
        return user

    async def update_role(self, user: User, role_name: str) -> User:
        role = await RoleService(self.db).get_by_name(role_name)
        if role is None:
            raise ValueError(f"Role not found: {role_name}")

        user.role_id = role.id
        user.role = role
        await self.db.flush()
        reloaded = await self.get_by_id(user.id)
        if reloaded is None:
            raise ValueError("User not found after role update")
        return reloaded

    async def list_users(self, *, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        total_result = await self.db.execute(select(func.count()).select_from(User))
        total = int(total_result.scalar_one())

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        users = list(result.scalars().all())
        return users, total

    @staticmethod
    def total_pages(total: int, page_size: int) -> int:
        return ceil(total / page_size) if total > 0 else 0
