from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_repository_forecast_endpoint():
    response = client.get("/api/v1/forecast/microsoft/vscode?horizon=180")
    assert response.status_code == 200
    data = response.json()

    assert data["owner"] == "microsoft"
    assert data["repo"] == "vscode"
    assert data["prediction_horizon_days"] == 180
    assert 0 <= data["derived_health_index"] <= 100
    assert 0.0 <= data["growth_probability"] <= 1.0
    assert 0.0 <= data["abandonment_probability"] <= 1.0
    assert 0.0 <= data["maintainer_retention_probability"] <= 1.0
    assert "narrative_summary" in data
    assert isinstance(data["top_drivers"], list)
    assert isinstance(data["top_risks"], list)
    assert data["model_version"] == "v1.0"
