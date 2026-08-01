from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.api.dependencies import _SNAPSHOT_SERVICE
from backend.app.main import app
from backend.app.snapshots.snapshot_builder import SnapshotBuilder

client = TestClient(app)


def test_get_repository_forecast_endpoint():
    builder = SnapshotBuilder()
    mock_snapshot = builder.build_snapshot_from_raw(
        {
            "name": "vscode",
            "owner": {"login": "microsoft"},
            "stargazers_count": 150000,
        },
        snapshot_time=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
    )

    with patch.object(_SNAPSHOT_SERVICE, "collect_and_build_snapshot", new=AsyncMock(return_value=mock_snapshot)), patch.object(_SNAPSHOT_SERVICE, "get_snapshot", new=AsyncMock(return_value=mock_snapshot)):
        response = client.get("/api/v1/forecast/microsoft/vscode?horizon=180")
        assert response.status_code == 200
        data = response.json()

        assert data["owner"] == "microsoft"
        assert data["repo"] == "vscode"
        assert data["prediction_horizon_days"] == 180
        assert 0 <= data["forecast"]["derived_health_index"] <= 100
        assert 0.0 <= data["forecast"]["growth_probability"] <= 1.0
        assert 0.0 <= data["forecast"]["abandonment_probability"] <= 1.0
        assert 0.0 <= data["forecast"]["maintainer_retention_probability"] <= 1.0
        assert "narrative_summary" in data
        assert isinstance(data["top_drivers"], list)
        assert isinstance(data["top_risks"], list)
        assert data["model_version"] == "v1.0"
