import os
from typing import Any

from pydantic import Field, model_validator

from backend.app.config.base import BaseAppSettings
from backend.app.config.models.app import AppConfig, Environment
from backend.app.config.models.cache import CacheConfig
from backend.app.config.models.database import DatabaseConfig
from backend.app.config.models.github import GitHubConfig
from backend.app.config.models.model import ModelConfig


class Settings(BaseAppSettings):
    """Root application configuration consolidating all subsystem settings."""

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)

    @model_validator(mode="before")
    @classmethod
    def populate_subsystem_env_vars(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        env = dict(os.environ)

        # App
        app_val = values.get("app")
        if app_val is None or isinstance(app_val, dict):
            app_dict = dict(app_val) if isinstance(app_val, dict) else {}
            if "ENVIRONMENT" in env:
                app_dict.setdefault("environment", env["ENVIRONMENT"])
            elif "APP_ENV" in env:
                app_dict.setdefault("environment", env["APP_ENV"])
            if "DEBUG" in env:
                app_dict.setdefault("debug", env["DEBUG"])
            if "APP_NAME" in env:
                app_dict.setdefault("app_name", env["APP_NAME"])
            if "API_V1_PREFIX" in env:
                app_dict.setdefault("api_v1_prefix", env["API_V1_PREFIX"])
            if "LOG_LEVEL" in env:
                app_dict.setdefault("log_level", env["LOG_LEVEL"])
            if "CORS_ORIGINS" in env:
                import json

                try:
                    app_dict.setdefault("cors_origins", json.loads(env["CORS_ORIGINS"]))
                except Exception:
                    app_dict.setdefault("cors_origins", [env["CORS_ORIGINS"]])
            values["app"] = app_dict

        # Database
        db_val = values.get("database")
        if db_val is None or isinstance(db_val, dict):
            db_dict = dict(db_val) if isinstance(db_val, dict) else {}
            if "DATABASE_URL" in env:
                db_dict.setdefault("url", env["DATABASE_URL"])
            elif "DB_URL" in env:
                db_dict.setdefault("url", env["DB_URL"])
            if "DATABASE_POOL_SIZE" in env:
                db_dict.setdefault("pool_size", env["DATABASE_POOL_SIZE"])
            if "DATABASE_MAX_OVERFLOW" in env:
                db_dict.setdefault("max_overflow", env["DATABASE_MAX_OVERFLOW"])
            if "DATABASE_POOL_TIMEOUT" in env:
                db_dict.setdefault("pool_timeout", env["DATABASE_POOL_TIMEOUT"])
            if "DATABASE_POOL_RECYCLE" in env:
                db_dict.setdefault("pool_recycle", env["DATABASE_POOL_RECYCLE"])
            if "DATABASE_POOL_USE_LIFO" in env:
                db_dict.setdefault("pool_use_lifo", env["DATABASE_POOL_USE_LIFO"])
            if "DATABASE_ECHO" in env:
                db_dict.setdefault("echo", env["DATABASE_ECHO"])
            values["database"] = db_dict

        # Cache
        cache_val = values.get("cache")
        if cache_val is None or isinstance(cache_val, dict):
            cache_dict = dict(cache_val) if isinstance(cache_val, dict) else {}
            if "REDIS_URL" in env:
                cache_dict.setdefault("redis_url", env["REDIS_URL"])
            if "REDIS_CACHE_TTL" in env:
                cache_dict.setdefault("redis_cache_ttl", env["REDIS_CACHE_TTL"])
            values["cache"] = cache_dict

        # GitHub
        gh_val = values.get("github")
        if gh_val is None or isinstance(gh_val, dict):
            gh_dict = dict(gh_val) if isinstance(gh_val, dict) else {}
            if "GITHUB_TOKEN" in env:
                gh_dict.setdefault("token", env["GITHUB_TOKEN"])
            if "GITHUB_API_VERSION" in env:
                gh_dict.setdefault("api_version", env["GITHUB_API_VERSION"])
            values["github"] = gh_dict

        # Model
        model_val = values.get("model")
        if model_val is None or isinstance(model_val, dict):
            model_dict = dict(model_val) if isinstance(model_val, dict) else {}
            if "MODEL_REGISTRY_PATH" in env:
                model_dict.setdefault("model_registry_path", env["MODEL_REGISTRY_PATH"])
            elif "MODEL_PATH" in env:
                model_dict.setdefault("model_registry_path", env["MODEL_PATH"])
            if "DEFAULT_MODEL_VERSION" in env:
                model_dict.setdefault("default_model_version", env["DEFAULT_MODEL_VERSION"])
            values["model"] = model_dict

        return values

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

    @property
    def LOG_LEVEL(self) -> str:
        return self.app.log_level

    @property
    def MODEL_REGISTRY_PATH(self) -> str:
        return self.model.model_registry_path

    @property
    def DEFAULT_MODEL_VERSION(self) -> str:
        return self.model.default_model_version

    @property
    def redis(self) -> CacheConfig:
        return self.cache

    @property
    def logging(self) -> AppConfig:
        return self.app


settings = Settings()
