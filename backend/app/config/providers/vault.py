from backend.app.config.providers.interface import SecretProvider


class VaultProvider(SecretProvider):
    """Secret provider implementation for external Vault secret store.

    Can be backed by in-memory dictionary or external secret store backends
    (e.g., HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager).
    """

    def __init__(self, vault_store: dict[str, str] | None = None) -> None:
        self._vault_store: dict[str, str] = vault_store or {}

    def get_secret(self, key: str) -> str | None:
        return self._vault_store.get(key)
