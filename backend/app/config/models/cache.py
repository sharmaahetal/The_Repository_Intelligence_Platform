from pydantic import Field

from backend.app.config.base import BaseAppSettings


class CacheConfig(BaseAppSettings):
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    default_cache_ttl: int = Field(default=3600, validation_alias="DEFAULT_CACHE_TTL")
