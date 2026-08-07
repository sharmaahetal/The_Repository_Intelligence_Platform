from enum import StrEnum

from pydantic import Field, model_validator

from backend.app.config.base import BaseAppSettings


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class AppConfig(BaseAppSettings):
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    app_name: str = "Repository Intelligence Platform"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    @model_validator(mode="after")
    def validate_production_cors(self) -> "AppConfig":
        if self.environment == Environment.PRODUCTION and "*" in self.cors_origins:
            raise ValueError(
                "Wildcard CORS origins ['*'] are strictly forbidden in production environment. "
                "Explicit origins must be specified."
            )
        return self
