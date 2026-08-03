import os
from unittest.mock import patch

import pytest
from pydantic import BaseModel, SecretStr, ValidationError

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


def test_subsystems_are_plain_basemodels():
    """Verify subsystems inherit from plain pydantic BaseModel, not BaseSettings."""
    assert issubclass(AppSettings, BaseModel)
    assert issubclass(DatabaseSettings, BaseModel)
    assert issubclass(GitHubSettings, BaseModel)
    assert issubclass(RedisSettings, BaseModel)
    assert issubclass(LoggingSettings, BaseModel)
    assert issubclass(ModelSettings, BaseModel)


def test_database_url_required_no_fallback():
    """Blocker 1: Database URL has no default. Missing DATABASE_URL must raise ValidationError."""
    with patch.dict(os.environ, {}, clear=True):
        if os.path.exists(".env"):
            with patch("os.path.exists", return_value=False):
                get_settings.cache_clear()
                with pytest.raises(ValidationError) as exc_info:
                    get_settings()
                assert "database" in str(exc_info.value)
        get_settings.cache_clear()


def test_environment_literal_validation():
    """Blocker 2: Environment must be Literal['development', 'testing', 'staging', 'production']."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://localhost:5432/test_db", "ENVIRONMENT": "invalid_env_name"},
        clear=True,
    ):
        get_settings.cache_clear()
        with pytest.raises(ValidationError) as exc_info:
            get_settings()
        assert "environment" in str(exc_info.value)
    get_settings.cache_clear()


def test_log_level_literal_validation():
    """Blocker 3: Log level must be Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']."""
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://localhost:5432/test_db", "LOG_LEVEL": "TRACE"},
        clear=True,
    ):
        get_settings.cache_clear()
        with pytest.raises(ValidationError) as exc_info:
            get_settings()
        assert "log_level" in str(exc_info.value)
    get_settings.cache_clear()


def test_secret_str_github_token():
    """Major 3: GitHub token uses SecretStr to prevent credential leakage."""
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql://localhost:5432/test_db",
            "GITHUB_TOKEN": "ghp_secret_token_123456789",
        },
        clear=True,
    ):
        get_settings.cache_clear()
        s = get_settings()
        assert isinstance(s.github.token, SecretStr)
        assert s.github.token.get_secret_value() == "ghp_secret_token_123456789"
        # Verify str representation is masked
        assert "ghp_secret_token_123456789" not in str(s.github.token)
    get_settings.cache_clear()


def test_settings_lru_cache_singleton():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
