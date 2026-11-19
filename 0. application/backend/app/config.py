from datetime import datetime
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "dev"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{(BACKEND_DIR / 'data' / 'freshcart.db').as_posix()}"
    JWT_SECRET: str = "freshcart-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    ACCOUNT_LOCK_MINUTES: int = 15
    MAX_FAILED_LOGINS: int = 5
    FIXED_NOW: str | None = None
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def fixed_now(self) -> datetime | None:
        if not self.FIXED_NOW:
            return None
        return datetime.fromisoformat(self.FIXED_NOW)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
