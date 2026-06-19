import json

from redis.asyncio import Redis

from app.core.config import get_settings
from app.schemas.product import ProductResponse

settings = get_settings()
CACHE_HEADER = "X-Cache"


class ProductCacheService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.ttl = settings.product_cache_ttl_seconds

    @staticmethod
    def cache_key(product_id: str) -> str:
        return f"product:{product_id}"

    async def get_product(self, product_id: str) -> ProductResponse | None:
        raw = await self.redis.get(self.cache_key(product_id))
        if raw is None:
            return None
        return ProductResponse.model_validate_json(raw)

    async def set_product(self, product: ProductResponse) -> None:
        key = self.cache_key(str(product.id))
        await self.redis.set(key, product.model_dump_json(), ex=self.ttl)

    async def invalidate(self, product_id: str) -> None:
        await self.redis.delete(self.cache_key(product_id))
