import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine
from app.core.logging_config import configure_logging
from app.core.redis import close_redis, get_redis
from app.routers import categories, products
from app.schemas.product import HealthResponse

settings = get_settings()
configure_logging(settings.environment)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (%s)", settings.app_name, settings.environment)
    await get_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Cache"],
)

app.include_router(products.router)
app.include_router(categories.router)


async def _probe_database() -> str:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


async def _probe_redis() -> str:
    try:
        client = await get_redis()
        return "ok" if await client.ping() else "error"
    except Exception:
        return "error"


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    database = await _probe_database()
    redis_status = await _probe_redis()
    overall = "ok" if database == "ok" and redis_status == "ok" else "degraded"
    return HealthResponse(status=overall, database=database, redis=redis_status)
