"""Configuration subsystem for Repository Intelligence Platform.

Centralizes application, database, cache, GitHub, logging, and ML model settings
into a unified, type-safe, validated, and cached configuration hierarchy.
"""

import os
from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

# Environment & Log Level Types
EnvironmentType = Literal["development", "testing", "staging", "production"]
LogLevelType = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


# ============================================================================
# Part 2 — Individual Settings Subsystem Classes (Plain Pydantic BaseModels)
# ============================================================================

class AppSettings(BaseModel):
    """Application runtime and metadata configuration."""

    app_name: str = Field(
        default="Repository Intelligence Platform",
        description="Public display name of the application.",
    )
    version: str = Field(
        default="1.0.0",
        description="Application release semantic version.",
    )
    environment: EnvironmentType = Field(
        default="development",
        description="Execution environment mode (development, testing, staging, production).",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode and detailed tracebacks.",
    )
class DatabaseSettings(BaseModel):
    """Relational database connection pool and engine configuration."""

    url: str = Field(
        default="sqlite+aiosqlite:///./data.db",
        description="Async database connection string URL.",
    )

    pool_size: int = Field(
        default=5,
        description="Connection pool size limit.",
    )
    max_overflow: int = Field(
        default=10,
        description="Maximum connection pool overflow limit.",
    )
    pool_timeout: int = Field(
        default=30,
        description="Connection pool timeout in seconds before raising an error.",
    )
    pool_recycle: int = Field(
        default=1800,
        description="Connection pool recycle window in seconds.",
    )
    pool_use_lifo: bool = Field(
        default=True,
        description="Enable LIFO connection reuse strategy for improved pool efficiency.",
    )
    echo: bool = Field(
        default=False,
        description="Enable SQL engine statement query logging.",
    )


class GitHubSettings(BaseModel):
    """GitHub API client authentication and API versioning configuration."""

    token: SecretStr | None = Field(
        default=None,
        description="GitHub Personal Access Token for rate limit authorization.",
    )
    api_version: str = Field(
        default="2022-11-28",
        description="GitHub REST API target spec header version.",
    )


class RedisSettings(BaseModel):
    """Redis cache connection and TTL configuration."""

    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis server connection URL.",
    )
    cache_ttl: int = Field(
        default=900,
        description="Default prediction report cache expiration TTL in seconds.",
    )


class LoggingSettings(BaseModel):
    """Logging level and telemetry formatting configuration."""

    log_level: LogLevelType = Field(
        default="INFO",
        description="Log output severity threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )


class ModelSettings(BaseModel):
    """Machine learning model registry and prediction configuration."""

    model_registry_path: str = Field(
        default="artifacts/registry",
        description="Filesystem path to versioned model artifact binaries.",
    )
    default_model_version: str = Field(
        default="v1.0",
        description="Default model artifact version identifier.",
    )


# Helper function to read environment map
def _load_env_map() -> dict[str, Any]:
    env_map: dict[str, Any] = dict(os.environ)
    if os.path.exists(".env"):
        try:
            with open(".env", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env_map.setdefault(k.strip(), v.strip().strip("\"'"))
        except Exception:
            pass
    return env_map


# ============================================================================
# Part 3 — Top-Level Settings Composition Class (BaseSettings Root)
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

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        class NestedFlatEnvSource(PydanticBaseSettingsSource):
            def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
                return None, "", False

            def __call__(self) -> dict[str, Any]:
                env = _load_env_map()
                d: dict[str, Any] = {}

                # App
                app_d: dict[str, Any] = {}
                if "APP_NAME" in env:
                    app_d["app_name"] = env["APP_NAME"]
                if "APP_VERSION" in env or "VERSION" in env:
                    app_d["version"] = env.get("APP_VERSION") or env.get("VERSION")
                if "ENVIRONMENT" in env or "APP_ENV" in env or "APP_ENVIRONMENT" in env:
                    app_d["environment"] = env.get("APP_ENVIRONMENT") or env.get("ENVIRONMENT") or env.get("APP_ENV")
                if "DEBUG" in env:
                    app_d["debug"] = str(env["DEBUG"]).lower() in ("true", "1", "t", "yes")
                if app_d:
                    d["app"] = app_d

                # Database
                db_d: dict[str, Any] = {}
                if "DATABASE_URL" in env:
                    db_d["url"] = env["DATABASE_URL"]
                if "DATABASE_POOL_SIZE" in env:
                    db_d["pool_size"] = int(env["DATABASE_POOL_SIZE"])
                if "DATABASE_MAX_OVERFLOW" in env:
                    db_d["max_overflow"] = int(env["DATABASE_MAX_OVERFLOW"])
                if "DATABASE_POOL_TIMEOUT" in env:
                    db_d["pool_timeout"] = int(env["DATABASE_POOL_TIMEOUT"])
                if "DATABASE_POOL_RECYCLE" in env:
                    db_d["pool_recycle"] = int(env["DATABASE_POOL_RECYCLE"])
                if "DATABASE_POOL_USE_LIFO" in env:
                    db_d["pool_use_lifo"] = str(env["DATABASE_POOL_USE_LIFO"]).lower() in ("true", "1", "t", "yes")
                if "DATABASE_ECHO" in env:
                    db_d["echo"] = str(env["DATABASE_ECHO"]).lower() in ("true", "1", "t", "yes")
                if db_d:
                    d["database"] = db_d


                # Redis
                redis_d: dict[str, Any] = {}
                if "REDIS_URL" in env:
                    redis_d["url"] = env["REDIS_URL"]
                if "REDIS_CACHE_TTL" in env:
                    redis_d["cache_ttl"] = int(env["REDIS_CACHE_TTL"])
                if redis_d:
                    d["redis"] = redis_d

                # GitHub
                gh_d: dict[str, Any] = {}
                if "GITHUB_TOKEN" in env and env["GITHUB_TOKEN"]:
                    gh_d["token"] = env["GITHUB_TOKEN"]
                if "GITHUB_API_VERSION" in env:
                    gh_d["api_version"] = env["GITHUB_API_VERSION"]
                if gh_d:
                    d["github"] = gh_d

                # Logging
                log_d: dict[str, Any] = {}
                if "LOG_LEVEL" in env:
                    log_d["log_level"] = env["LOG_LEVEL"]
                if log_d:
                    d["logging"] = log_d

                # Model
                model_d: dict[str, Any] = {}
                if "MODEL_REGISTRY_PATH" in env or "MODEL_PATH" in env:
                    model_d["model_registry_path"] = env.get("MODEL_REGISTRY_PATH") or env.get("MODEL_PATH")
                if "DEFAULT_MODEL_VERSION" in env:
                    model_d["default_model_version"] = env["DEFAULT_MODEL_VERSION"]
                if model_d:
                    d["model"] = model_d

                return d


        return (init_settings, NestedFlatEnvSource(settings_cls), env_settings, dotenv_settings)


# ============================================================================
# Part 4 — LRU Cached Singleton Accessor
# ============================================================================

@lru_cache
def get_settings() -> Settings:
    """Retrieve or initialize the cached application Settings singleton."""
    return Settings()


settings: Settings = get_settings()
