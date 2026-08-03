import os
from unittest.mock import patch

from backend.app.core.settings import (
    AppSettings,
    DatabaseSettings,
    GitHubSettings,
    LoggingSettings,
    ModelSettings,
    RedisSettings,
    Settings,
    get_settings,
    settings,
)


def test_settings_default_instantiation():
    s = get_settings()
    assert s is settings
    assert isinstance(s.app, AppSettings)
    assert isinstance(s.database, DatabaseSettings)
    assert isinstance(s.redis, RedisSettings)
    assert isinstance(s.github, GitHubSettings)
    assert isinstance(s.logging, LoggingSettings)
    assert isinstance(s.model, ModelSettings)

    assert s.app.app_name == "Repository Intelligence Platform"
    assert s.app.version == "1.0.0"
    assert s.database.url.startswith(("sqlite", "postgresql"))
    assert s.redis.url.startswith("redis://")
    assert s.logging.log_level == "INFO"
    assert s.model.model_registry_path == "artifacts/registry"


def test_settings_lru_cache_singleton():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_environment_variable_override():
    with patch.dict(
        os.environ,
        {
            "APP_NAME": "Custom RIP Platform",
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/custom_db",
            "REDIS_URL": "redis://cache.internal:6379/1",
            "LOG_LEVEL": "DEBUG",
        },
        clear=False,
    ):
        # Clear lru_cache for custom test instance
        get_settings.cache_clear()
        custom_settings = get_settings()

        assert custom_settings.app.app_name == "Custom RIP Platform"
        assert custom_settings.database.url == "postgresql+asyncpg://user:pass@localhost:5432/custom_db"
        assert custom_settings.redis.url == "redis://cache.internal:6379/1"
        assert custom_settings.logging.log_level == "DEBUG"

        # Restore singleton
        get_settings.cache_clear()
