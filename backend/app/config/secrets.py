from backend.app.config.providers.env import EnvProvider
from backend.app.config.providers.interface import SecretProvider
from backend.app.config.providers.vault import VaultProvider
from backend.app.logging import logger


class MissingSecretError(Exception):
    """Raised when a required secret cannot be resolved from any registered SecretProvider."""

    pass


class SecretsManager:
    """Manages secret resolution across pluggable SecretProvider backends."""

    def __init__(self, providers: list[SecretProvider] | None = None) -> None:
        self.providers: list[SecretProvider] = (
            providers if providers is not None else [EnvProvider(), VaultProvider()]
        )

    def get_secret(self, key: str, default: str | None = None, required: bool = False) -> str:
        """Resolves secret from registered providers in priority order.

        Args:
            key: Secret key to retrieve.
            default: Default value if not found in any provider.
            required: If True, raises MissingSecretError when key is not found.

        Raises:
            MissingSecretError: If key is required or no default is provided and key is missing.
        """
        for provider in self.providers:
            val = provider.get_secret(key)
            if val is not None:
                return val

        if required or default is None:
            logger.error("Required secret key not found in any provider", extra={"key": key})
            raise MissingSecretError(
                f"Secret key '{key}' was not found in any registered SecretProvider."
            )

        logger.debug("Secret key not found, returning default fallback", extra={"key": key})
        return default


# Global secrets manager instance
secrets_manager = SecretsManager()
