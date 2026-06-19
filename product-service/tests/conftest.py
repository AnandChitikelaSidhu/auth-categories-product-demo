import os
import subprocess
import sys
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DB_NAME = "product_db_test"
TEST_DB_USER = os.getenv("USER", "anandchitikela")
TEST_DB_URL = f"postgresql+asyncpg://{TEST_DB_USER}@localhost:5432/{TEST_DB_NAME}"
JWT_SECRET = "test-secret-key-for-pytest-only"

os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["JWT_SECRET_KEY"] = JWT_SECRET
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["PRODUCT_CACHE_TTL_SECONDS"] = "300"

from app.core.config import get_settings

get_settings.cache_clear()

import app.core.redis as redis_module
import app.core.database as database
from app.main import app

settings = get_settings()


def _ensure_test_database() -> None:
    check = subprocess.run(
        ["psql", "-h", "localhost", "-U", TEST_DB_USER, "-d", "postgres", "-tc",
         f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'"],
        capture_output=True, text=True,
    )
    if check.stdout.strip() != "1":
        subprocess.run(
            ["psql", "-h", "localhost", "-U", TEST_DB_USER, "-d", "postgres", "-c",
             f'CREATE DATABASE "{TEST_DB_NAME}"'],
            check=True,
        )


def _run_migrations() -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_DB_URL
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT, env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    _ensure_test_database()
    _run_migrations()


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, pool_pre_ping=True)
    database.engine = engine
    database.AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield engine
    await engine.dispose()


async def _truncate_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE products, categories RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def fake_redis() -> AsyncGenerator[FakeRedis, None]:
    client = FakeRedis(decode_responses=True)
    redis_module.redis_client = client
    yield client
    await client.flushall()
    await client.aclose()
    redis_module.redis_client = None


@pytest_asyncio.fixture(autouse=True)
async def clean_state(test_engine, fake_redis):
    await _truncate_tables(test_engine)
    await fake_redis.flushall()
    yield
    await _truncate_tables(test_engine)
    await fake_redis.flushall()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with database.AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client


def make_token(role: str = "admin", user_id: UUID | None = None) -> str:
    uid = user_id or uuid4()
    payload = {
        "sub": str(uid),
        "email": "admin@example.com",
        "role": role,
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token('admin')}"}


@pytest.fixture
def customer_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token('customer')}"}
