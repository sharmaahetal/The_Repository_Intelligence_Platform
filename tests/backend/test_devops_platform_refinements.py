from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_liveness_readiness_and_startup_probes():
    # 1. Live probe
    res_live = client.get("/api/v1/health/live")
    assert res_live.status_code == 200
    data_live = res_live.json()
    assert data_live["status"] == "ok"

    # 2. Ready probe
    res_ready = client.get("/api/v1/health/ready")
    assert res_ready.status_code == 200
    data_ready = res_ready.json()
    assert data_ready["status"] in ("ready", "degraded")
    assert "model_loaded" in data_ready

    # 3. Startup probe
    res_startup = client.get("/api/v1/health/startup")
    assert res_startup.status_code == 200
    data_startup = res_startup.json()
    assert data_startup["status"] == "started"
    assert data_startup["bootstrap_completed"] is True


def test_security_headers_middleware():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
