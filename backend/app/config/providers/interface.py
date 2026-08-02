from abc import ABC, abstractmethod


class SecretProvider(ABC):
    """Abstract interface for secret resolution providers."""

    @abstractmethod
    def get_secret(self, key: str) -> str | None:
        """Retrieve secret value for key, returning None if key is not found."""
        pass
