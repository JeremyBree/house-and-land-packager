"""Application configuration via environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://hlp:hlp_dev@localhost:5432/hlp_dev"
    secret_key: str = "change-me"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 hours
    jwt_expiry_minutes: int = 1440  # legacy, retained for backwards-compat
    bcrypt_rounds: int = 12
    anthropic_api_key: str = ""
    storage_base_path: str = "/data/storage"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
