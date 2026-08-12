import os
from unittest.mock import patch

from backend.app.config import settings
from backend.app.config.models import (
    AppConfig,
    CacheConfig,
    DatabaseConfig,
    GitHubConfig,
    ModelConfig,
)
from backend.app.config.settings import Settings


def test_subsystem_configs_exist():
    """Verify consolidated Settings contains all subsystem configs."""
    s = Settings()
    assert isinstance(s.app, AppConfig)
    assert isinstance(s.database, DatabaseConfig)
    assert isinstance(s.github, GitHubConfig)
    assert isinstance(s.cache, CacheConfig)
    assert isinstance(s.model, ModelConfig)


def test_database_url_default():
    """Verify database URL defaults and environment overrides."""
    with patch.dict(os.environ, {"DATABASE_URL": "sqlite+aiosqlite:///./test_override.db"}, clear=True):
        s = Settings()
        assert s.database.url == "sqlite+aiosqlite:///./test_override.db"


def test_environment_and_log_level_overrides():
    """Verify environment and log_level settings configuration."""
    with patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "production",
            "CORS_ORIGINS": '["https://app.example.com"]',
            "LOG_LEVEL": "WARNING",
        },
        clear=True,
    ):
        s = Settings()
        assert s.app.environment == "production"
        assert s.app.log_level == "WARNING"


def test_backwards_compatibility_properties():
    """Verify top-level backward compatibility property accessors on Settings."""
    assert settings.DATABASE_URL is not None
    assert settings.REDIS_URL is not None
    assert settings.APP_NAME is not None
    assert settings.MODEL_REGISTRY_PATH is not None
    assert settings.DEFAULT_MODEL_VERSION is not None
    assert settings.redis is not None
