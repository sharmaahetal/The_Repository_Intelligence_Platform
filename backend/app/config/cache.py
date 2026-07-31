from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    DEFAULT_CACHE_TTL: int = 3600  # 1 hour TTL for report responses

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


cache_settings = CacheSettings()
