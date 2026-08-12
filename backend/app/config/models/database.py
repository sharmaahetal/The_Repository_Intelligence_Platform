from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DatabaseConfig(BaseModel):
    """Relational database connection pool and engine configuration."""

    model_config = ConfigDict(populate_by_name=True)

    url: str = Field(
        default="sqlite+aiosqlite:///./data.db",
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL", "DATABASE__URL"),
    )
    pool_size: int = Field(
        default=5,
        validation_alias=AliasChoices("DATABASE_POOL_SIZE", "DB_POOL_SIZE", "DATABASE__POOL_SIZE"),
    )
    max_overflow: int = Field(
        default=10,
        validation_alias=AliasChoices("DATABASE_MAX_OVERFLOW", "DB_MAX_OVERFLOW", "DATABASE__MAX_OVERFLOW"),
    )
    pool_timeout: int = Field(
        default=30,
        validation_alias=AliasChoices("DATABASE_POOL_TIMEOUT", "DATABASE__POOL_TIMEOUT"),
    )
    pool_recycle: int = Field(
        default=1800,
        validation_alias=AliasChoices("DATABASE_POOL_RECYCLE", "DATABASE__POOL_RECYCLE"),
    )
    pool_use_lifo: bool = Field(
        default=True,
        validation_alias=AliasChoices("DATABASE_POOL_USE_LIFO", "DATABASE__POOL_USE_LIFO"),
    )
    echo: bool = Field(
        default=False,
        validation_alias=AliasChoices("DATABASE_ECHO", "DB_ECHO", "DATABASE__ECHO"),
    )
