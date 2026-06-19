import os
import subprocess
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DB_NAME = "auth_db_test"
TEST_DB_USER = os.getenv("USER", "anandchitikela")
TEST_DB_URL = f"postgresql+asyncpg://{TEST_DB_USER}@localhost:5432/{TEST_DB_NAME}"
TEST_REDIS_URL = "redis://localhost:6379/15"

os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["REDIS_URL"] = TEST_REDIS_URL
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["LOGIN_MAX_ATTEMPTS"] = "5"
os.environ["LOGIN_LOCKOUT_MINUTES"] = "15"

from app.core.config import get_settings

get_settings.cache_clear()

import app.core.database as database
import app.core.redis as redis_module
from app.main import app


def _ensure_test_database() -> None:
    check = subprocess.run(
        [
            "psql",
            "-h",
            "localhost",
            "-U",
            TEST_DB_USER,
            "-d",
            "postgres",
            "-tc",
            f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if check.stdout.strip() != "1":
        subprocess.run(
            [
                "psql",
                "-h",
                "localhost",
                "-U",
                TEST_DB_USER,
                "-d",
                "postgres",
                "-c",
                f'CREATE DATABASE "{TEST_DB_NAME}"',
            ],
            check=True,
        )


def _run_alembic_upgrade() -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = TEST_DB_URL
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Alembic migration failed:\n{result.stderr}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    _ensure_test_database()
    _run_alembic_upgrade()


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, pool_pre_ping=True)
    database.engine = engine
    database.AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield engine
    await engine.dispose()


async def _truncate_users(engine) -> None:
    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))


async def _flush_test_redis() -> None:
    redis = Redis.from_url(TEST_REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        await redis.flushdb()
    finally:
        await redis.aclose()
    redis_module.redis_client = None


@pytest_asyncio.fixture(autouse=True)
async def clean_state(test_engine) -> AsyncGenerator[None, None]:
    await _truncate_users(test_engine)
    await _flush_test_redis()
    yield
    await _truncate_users(test_engine)
    await _flush_test_redis()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with database.AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    client = Redis.from_url(TEST_REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client


@pytest.fixture
def user_payload() -> dict[str, str]:
    return {
        "email": "testuser@example.com",
        "password": "Password1",
        "full_name": "Test User",
    }
