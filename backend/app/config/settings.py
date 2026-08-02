from pydantic import Field

from backend.app.config.base import BaseAppSettings
from backend.app.config.models.app import AppConfig, Environment
from backend.app.config.models.cache import CacheConfig
from backend.app.config.models.database import DatabaseConfig
from backend.app.config.models.github import GitHubConfig


class Settings(BaseAppSettings):
    """Root application configuration consolidating all subsystem settings."""

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # Backwards-compatibility property accessors
    @property
    def CORS_ORIGINS(self) -> list[str]:
        return self.app.cors_origins

    @property
    def APP_NAME(self) -> str:
        return self.app.app_name

    @property
    def ENVIRONMENT(self) -> Environment:
        return self.app.environment

    @property
    def DEBUG(self) -> bool:
        return self.app.debug

    @property
    def API_V1_PREFIX(self) -> str:
        return self.app.api_v1_prefix

    @property
    def DATABASE_URL(self) -> str:
        return self.database.url

    @property
    def GITHUB_TOKEN(self) -> str | None:
        return self.github.token

    @property
    def REDIS_URL(self) -> str:
        return self.cache.redis_url


settings = Settings()
