from datetime import UTC, datetime
from uuid import UUID, uuid4

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    is_token_valid,
)
from app.models.user import User
from app.schemas.auth import TokenResponse

settings = get_settings()


class TokenService:
    REFRESH_PREFIX = "refresh_token:"
    REFRESH_BLACKLIST_PREFIX = "refresh_blacklist:"
    ACCESS_BLACKLIST_PREFIX = "access_blacklist:"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.refresh_ttl_seconds = settings.refresh_token_expire_days * 24 * 60 * 60
        self.access_ttl_seconds = settings.access_token_expire_minutes * 60

    def _refresh_key(self, jti: str) -> str:
        return f"{self.REFRESH_PREFIX}{jti}"

    def _refresh_blacklist_key(self, jti: str) -> str:
        return f"{self.REFRESH_BLACKLIST_PREFIX}{jti}"

    def _access_blacklist_key(self, jti: str) -> str:
        return f"{self.ACCESS_BLACKLIST_PREFIX}{jti}"

    def _ttl_from_exp(self, exp: int | None, default_ttl: int) -> int:
        if exp is None:
            return default_ttl
        expires_at = datetime.fromtimestamp(exp, tz=UTC)
        return max(int((expires_at - datetime.now(UTC)).total_seconds()), 1)

    async def issue_tokens(self, user: User) -> TokenResponse:
        access_jti = str(uuid4())
        refresh_jti = str(uuid4())
        access_token = create_access_token(
            subject=user.id,
            email=user.email,
            role=user.role.value,
            jti=access_jti,
        )
        refresh_token = create_refresh_token(subject=user.id, jti=refresh_jti)
        await self.redis.setex(
            self._refresh_key(refresh_jti),
            self.refresh_ttl_seconds,
            str(user.id),
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def _decode_refresh_payload(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not is_token_valid(payload, "refresh"):
            raise ValueError("Invalid refresh token type")

        jti = payload.get("jti")
        if not jti:
            raise ValueError("Refresh token missing jti")

        return payload

    async def validate_refresh_token(self, refresh_token: str) -> UUID:
        payload = await self._decode_refresh_payload(refresh_token)
        jti = payload["jti"]

        if await self.redis.exists(self._refresh_blacklist_key(jti)):
            raise ValueError("Refresh token has been revoked")

        stored_user_id = await self.redis.get(self._refresh_key(jti))
        if stored_user_id is None:
            raise ValueError("Refresh token is invalid or expired")

        user_id = UUID(payload["sub"])
        if stored_user_id != str(user_id):
            raise ValueError("Refresh token mismatch")

        return user_id

    async def rotate_refresh_token(self, refresh_token: str, user: User) -> TokenResponse:
        payload = await self._decode_refresh_payload(refresh_token)
        old_jti = payload["jti"]

        await self.validate_refresh_token(refresh_token)
        await self._revoke_refresh_jti(old_jti, payload.get("exp"))
        return await self.issue_tokens(user)

    async def _decode_access_payload(self, access_token: str) -> dict:
        payload = decode_token(access_token)
        if not is_token_valid(payload, "access"):
            raise ValueError("Invalid access token type")

        jti = payload.get("jti")
        if not jti:
            raise ValueError("Access token missing jti")

        return payload

    async def is_access_token_revoked(self, jti: str) -> bool:
        return bool(await self.redis.exists(self._access_blacklist_key(jti)))

    async def blacklist_access_token(self, access_token: str) -> None:
        payload = await self._decode_access_payload(access_token)
        ttl = self._ttl_from_exp(payload.get("exp"), self.access_ttl_seconds)
        await self.redis.setex(self._access_blacklist_key(payload["jti"]), ttl, "1")

    async def _revoke_refresh_jti(self, jti: str, exp: int | None) -> None:
        await self.redis.delete(self._refresh_key(jti))
        ttl = self._ttl_from_exp(exp, self.refresh_ttl_seconds)
        await self.redis.setex(self._refresh_blacklist_key(jti), ttl, "1")

    async def blacklist_refresh_token(self, refresh_token: str) -> None:
        payload = await self._decode_refresh_payload(refresh_token)
        await self._revoke_refresh_jti(payload["jti"], payload.get("exp"))
