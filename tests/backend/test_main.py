from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /health returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fastapi_app_title_and_version():
    """Verify FastAPI application title and version configuration."""
    assert app.title == "Repository Intelligence Platform"
    assert app.version == "1.0.0"
