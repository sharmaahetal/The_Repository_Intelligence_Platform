"""Configuration subsystem for Repository Intelligence Platform.

Centralizes application, database, cache, GitHub, logging, and ML model settings
into a unified, type-safe, validated, and cached configuration hierarchy.
"""

from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================================
# Part 2 — Individual Settings Subsystem Classes
# ============================================================================

class AppSettings(BaseSettings):
    """Application runtime and metadata configuration."""

    app_name: str = Field(
        default="Repository Intelligence Platform",
        validation_alias=AliasChoices("APP_NAME", "app_name"),
        description="Public display name of the application.",
    )
    version: str = Field(
        default="1.0.0",
        validation_alias=AliasChoices("APP_VERSION", "VERSION", "version"),
        description="Application release semantic version.",
    )
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENVIRONMENT", "ENVIRONMENT", "APP_ENV", "environment"),
        description="Execution environment mode (development, staging, production).",
    )
    debug: bool = Field(
        default=False,
        validation_alias=AliasChoices("DEBUG", "debug"),
        description="Enable debug mode and detailed tracebacks.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DatabaseSettings(BaseSettings):
    """Relational database connection pool and engine configuration."""

    url: str = Field(
        default="sqlite+aiosqlite:///./data.db",
        validation_alias=AliasChoices("DATABASE_URL", "url"),
        description="Async database connection string URL.",
    )
    pool_size: int = Field(
        default=5,
        validation_alias=AliasChoices("DATABASE_POOL_SIZE", "POOL_SIZE", "pool_size"),
        description="Connection pool size limit.",
    )
    max_overflow: int = Field(
        default=10,
        validation_alias=AliasChoices("DATABASE_MAX_OVERFLOW", "MAX_OVERFLOW", "max_overflow"),
        description="Maximum connection pool overflow limit.",
    )
    echo: bool = Field(
        default=False,
        validation_alias=AliasChoices("DATABASE_ECHO", "ECHO_SQL", "echo"),
        description="Enable SQL engine statement query logging.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class GitHubSettings(BaseSettings):
    """GitHub API client authentication and API versioning configuration."""

    token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GITHUB_TOKEN", "token"),
        description="GitHub Personal Access Token for rate limit authorization.",
    )
    api_version: str = Field(
        default="2022-11-28",
        validation_alias=AliasChoices("GITHUB_API_VERSION", "API_VERSION", "api_version"),
        description="GitHub REST API target spec header version.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    """Redis cache connection and TTL configuration."""

    url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "url"),
        description="Redis server connection URL.",
    )
    cache_ttl: int = Field(
        default=900,
        validation_alias=AliasChoices("REDIS_CACHE_TTL", "CACHE_TTL", "cache_ttl"),
        description="Default prediction report cache expiration TTL in seconds.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LoggingSettings(BaseSettings):
    """Logging level and telemetry formatting configuration."""

    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL", "log_level"),
        description="Log output severity threshold (DEBUG, INFO, WARNING, ERROR).",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ModelSettings(BaseSettings):
    """Machine learning model registry and prediction configuration."""

    model_registry_path: str = Field(
        default="artifacts/registry",
        validation_alias=AliasChoices("MODEL_REGISTRY_PATH", "MODEL_PATH", "model_registry_path"),
        description="Filesystem path to versioned model artifact binaries.",
    )
    default_model_version: str = Field(
        default="v1.0",
        validation_alias=AliasChoices("DEFAULT_MODEL_VERSION", "MODEL_VERSION", "default_model_version"),
        description="Default model artifact version identifier.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ============================================================================
# Part 3 — Top-Level Settings Composition Class
# ============================================================================

class Settings(BaseSettings):
    """Consolidated root application configuration model."""

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )


# ============================================================================
# Part 4 — LRU Cached Singleton Accessor
# ============================================================================

@lru_cache
def get_settings() -> Settings:
    """Retrieve or initialize the cached application Settings singleton."""
    return Settings()


settings: Settings = get_settings()
