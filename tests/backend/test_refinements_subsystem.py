import pytest

from backend.app.config import AppConfig, Environment, MissingSecretError, SecretsManager, settings
from backend.app.config.providers import EnvProvider, VaultProvider
from backend.app.ml.canary import CanaryDeploymentManager
from backend.app.models.lineage import DataLineage
from backend.app.tasks.queue import TaskQueue


def test_secrets_manager_resolution(monkeypatch):
    vault = VaultProvider({"CUSTOM_VAULT_KEY": "vault_secret_val"})
    secrets = SecretsManager(providers=[EnvProvider(), vault])

    # Default resolution when key absent
    val = secrets.get_secret("NON_EXISTENT_KEY", default="default_fallback")
    assert val == "default_fallback"

    # Vault provider resolution
    vault_val = secrets.get_secret("CUSTOM_VAULT_KEY")
    assert vault_val == "vault_secret_val"

    # MissingSecretError when key missing and required/un-defaulted
    with pytest.raises(MissingSecretError):
        secrets.get_secret("MISSING_REQUIRED_KEY", required=True)

    with pytest.raises(MissingSecretError):
        secrets.get_secret("MISSING_REQUIRED_KEY", default=None)

    # OS env provider resolution
    monkeypatch.setenv("GITHUB_TOKEN", "pat_token_test_123")
    token = secrets.get_secret("GITHUB_TOKEN")
    assert token == "pat_token_test_123"


def test_unified_settings_structure():
    assert settings.app.environment in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION, Environment.TESTING]
    assert isinstance(settings.database.url, str)
    assert isinstance(settings.cache.redis_url, str)
    assert isinstance(settings.github.api_url, str)
    assert settings.database.url == settings.DATABASE_URL
    assert settings.app.cors_origins == settings.CORS_ORIGINS


def test_production_cors_validation():
    # Development allows wildcard
    dev_config = AppConfig(environment=Environment.DEVELOPMENT, cors_origins=["*"])
    assert dev_config.cors_origins == ["*"]

    # Production rejects wildcard CORS
    with pytest.raises(ValueError, match="Wildcard CORS origins"):
        AppConfig(environment=Environment.PRODUCTION, cors_origins=["*"])

    # Production allows explicit origins
    prod_config = AppConfig(environment=Environment.PRODUCTION, cors_origins=["https://app.example.com"])
    assert prod_config.cors_origins == ["https://app.example.com"]


@pytest.mark.asyncio
async def test_task_queue_async_execution():
    queue = TaskQueue()

    async def mock_handler(payload: dict):
        return {"processed_repo": payload["repo"]}

    queue.register_handler("compute_features", mock_handler)
    task_id = await queue.enqueue("compute_features", {"repo": "facebook/react"})

    processed = await queue.process_next()
    assert processed is True

    status = queue.get_task_status(task_id)
    assert status is not None
    assert status.status == "completed"
    assert status.result == {"processed_repo": "facebook/react"}


def test_canary_deployment_routing():
    canary = CanaryDeploymentManager(challenger_traffic_pct=0.20)
    routed = [canary.route_request("v1.0", "v2.0-candidate")[1] for _ in range(100)]

    assert "champion" in routed
    metrics = canary.get_traffic_metrics()
    assert metrics["total_requests_routed"] == 100


def test_data_lineage_trace_integrity():
    lineage = DataLineage(model_version="v1.0", dataset_version="v1.0")
    assert lineage.prediction_id != ""
    assert lineage.model_version == "v1.0"
    assert lineage.git_commit != ""
