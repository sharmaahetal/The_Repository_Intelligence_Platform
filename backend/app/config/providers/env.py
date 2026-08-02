import os

from backend.app.config.providers.interface import SecretProvider


class EnvProvider(SecretProvider):
    """Secret provider reading directly from OS environment variables."""

    def get_secret(self, key: str) -> str | None:
        return os.environ.get(key)
