from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


class RateLimitService:
    LOGIN_FAIL_PREFIX = "login_fail:"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.lockout_seconds = settings.login_lockout_minutes * 60
        self.max_attempts = settings.login_max_attempts

    def _login_fail_key(self, email: str) -> str:
        return f"{self.LOGIN_FAIL_PREFIX}{email.lower()}"

    async def is_login_locked(self, email: str) -> bool:
        attempts = await self.redis.get(self._login_fail_key(email))
        print(f"attempts: {attempts}")
        if attempts is None:
            return False
        return int(attempts) >= self.max_attempts

    async def record_failed_login(self, email: str) -> int:
        key = self._login_fail_key(email)
        attempts = await self.redis.incr(key)
        print(f"attempts: {attempts}")
        if attempts == 1:
            await self.redis.expire(key, self.lockout_seconds)
        return int(attempts)

    async def clear_failed_logins(self, email: str) -> None:
        await self.redis.delete(self._login_fail_key(email))
