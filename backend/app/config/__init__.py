from backend.app.config.models import (
    AppConfig,
    CacheConfig,
    DatabaseConfig,
    Environment,
    GitHubConfig,
)
from backend.app.config.secrets import MissingSecretError, SecretsManager, secrets_manager
from backend.app.config.settings import settings

# Backwards compatible alias pointers to sub-configs on root settings
db_settings = settings.database
cache_settings = settings.cache
github_settings = settings.github

__all__ = [
    "settings",
    "secrets_manager",
    "SecretsManager",
    "MissingSecretError",
    "Environment",
    "AppConfig",
    "DatabaseConfig",
    "GitHubConfig",
    "CacheConfig",
    "db_settings",
    "cache_settings",
    "github_settings",
]
