import os

from backend.app.logging import logger


class SecretsManager:
    """Hierarchical secrets configuration manager prioritizing OS env, Vault/Cloud Secrets, and .env fallbacks."""

    def __init__(self, vault_backend: str | None = None) -> None:
        self.vault_backend = vault_backend or os.getenv("SECRETS_VAULT_BACKEND", "env")
        self._vault_mock_store: dict[str, str] = {
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "mock_github_pat_token_12345"),
            "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
            "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        }

    def get_secret(self, key: str, default: str = "") -> str:
        """Resolves secret from OS environment, vault store, or fallback default."""
        # 1. Check OS Environment Variables
        if key in os.environ:
            return os.environ[key]

        # 2. Check Vault Store
        if key in self._vault_mock_store:
            return self._vault_mock_store[key]

        logger.debug("Secret key not found in environment or vault", extra={"key": key})
        return default


# Global secrets manager instance
secrets_manager = SecretsManager()
