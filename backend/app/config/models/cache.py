from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CacheConfig(BaseModel):
    """Redis cache connection and TTL configuration."""

    model_config = ConfigDict(populate_by_name=True)

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "CACHE__REDIS_URL"),
    )
    redis_cache_ttl: int = Field(
        default=900,
        validation_alias=AliasChoices("REDIS_CACHE_TTL", "DEFAULT_CACHE_TTL", "CACHE__REDIS_CACHE_TTL"),
    )

    @property
    def url(self) -> str:
        return self.redis_url

    @property
    def cache_ttl(self) -> int:
        return self.redis_cache_ttl
