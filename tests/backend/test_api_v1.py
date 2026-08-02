from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.api.dependencies import _SNAPSHOT_SERVICE, get_forecast_service
from backend.app.api.exceptions import RepositoryNotFoundError
from backend.app.main import app
from backend.app.snapshots.snapshot_builder import SnapshotBuilder

client = TestClient(app)


def test_health_liveness_endpoint():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_health_readiness_endpoint():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_loaded"] is True
    assert data["registry_available"] is True


def test_forecast_caching_behavior():
    builder = SnapshotBuilder()
    mock_snapshot = builder.build_snapshot_from_raw(
        {
            "name": "go",
            "owner": {"login": "golang"},
            "stargazers_count": 120000,
        },
        snapshot_time=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
    )

    with (
        patch.object(
            _SNAPSHOT_SERVICE,
            "collect_and_build_snapshot",
            new=AsyncMock(return_value=mock_snapshot),
        ),
        patch.object(_SNAPSHOT_SERVICE, "get_snapshot", new=AsyncMock(return_value=mock_snapshot)),
    ):
        # 1. First call: cache miss -> cached = False
        res1 = client.get("/api/v1/forecast/golang/go?horizon=180")
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["cached"] is False

        # 2. Second call: cache hit -> cached = True
        res2 = client.get("/api/v1/forecast/golang/go?horizon=180")
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2["cached"] is True


def test_repository_not_found_exception_handling():
    class MockErrorService:
        async def get_forecast(
            self, owner: str, repo: str, horizon: int = 180, model_version: str = "v1.0"
        ):
            raise RepositoryNotFoundError(
                f"Repository '{owner}/{repo}' was not found on GitHub.",
                details={"owner": owner, "repo": repo},
            )

    app.dependency_overrides[get_forecast_service] = lambda: MockErrorService()

    try:
        response = client.get("/api/v1/forecast/nonexistent/fake_repo")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "REPOSITORY_NOT_FOUND"
        assert "not found" in data["message"]
    finally:
        app.dependency_overrides.clear()
