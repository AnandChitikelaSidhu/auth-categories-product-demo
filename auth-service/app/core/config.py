from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Auth Service"
    environment: Literal["development", "production"] = "development"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")

    jwt_secret_key: str = Field(default="change-me-in-production-use-a-long-random-string")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    bcrypt_rounds: int = 12

    login_max_attempts: int = 5
    login_lockout_minutes: int = 15

    @model_validator(mode="after")
    def sync_debug_with_environment(self) -> "Settings":
        self.debug = self.environment == "development"
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
