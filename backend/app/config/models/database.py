from pydantic import Field

from backend.app.config.base import BaseAppSettings


class DatabaseConfig(BaseAppSettings):
    url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/rip_db",
        validation_alias="DATABASE_URL",
    )
    pool_size: int = Field(default=20, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, validation_alias="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, validation_alias="DB_ECHO")
