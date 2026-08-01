from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_prometheus_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    text = response.text

    assert "# HELP rip_requests_total" in text
    assert "# TYPE rip_requests_total counter" in text
    assert "rip_requests_total" in text
    assert "rip_cache_hits_total" in text
    assert "rip_cache_misses_total" in text
    assert "rip_cache_hit_ratio" in text
