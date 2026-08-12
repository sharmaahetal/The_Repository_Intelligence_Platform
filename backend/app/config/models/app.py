from enum import StrEnum

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class AppConfig(BaseModel):
    """General application settings."""

    model_config = ConfigDict(populate_by_name=True)

    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV", "APP_ENVIRONMENT", "APP__ENVIRONMENT"),
    )
    debug: bool = Field(
        default=True,
        validation_alias=AliasChoices("DEBUG", "APP__DEBUG"),
    )
    app_name: str = Field(
        default="Repository Intelligence Platform",
        validation_alias=AliasChoices("APP_NAME", "APP__APP_NAME"),
    )
    api_v1_prefix: str = Field(
        default="/api/v1",
        validation_alias=AliasChoices("API_V1_PREFIX", "APP__API_V1_PREFIX"),
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        validation_alias=AliasChoices("CORS_ORIGINS", "APP__CORS_ORIGINS"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL", "APP__LOG_LEVEL"),
    )

    @model_validator(mode="after")
    def validate_production_cors(self) -> "AppConfig":
        env_str = str(self.environment).lower()
        if env_str == "production" and "*" in self.cors_origins:
            raise ValueError(
                "Wildcard CORS origins ['*'] are strictly forbidden in production environment. "
                "Explicit origins must be specified."
            )
        return self
