import json
import logging
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.app.api.exceptions import PredictionError, register_exception_handlers
from backend.app.logging import (
    TelemetryMiddleware,
    bind_contextvars,
    clear_request_context,
    get_request_context,
    log_duration,
    log_execution_time,
    logger,
    redact_sensitive_data,
    set_request_context,
)
from backend.app.logging.formatter import JSONFormatter


def test_contextvars_propagation():
    clear_request_context()
    assert get_request_context() == {}

    set_request_context(request_id="req_test_123", repository="facebook/react")
    ctx = get_request_context()
    assert ctx["request_id"] == "req_test_123"
    assert ctx["repository"] == "facebook/react"

    bind_contextvars(model_version="v2.0")
    ctx_updated = get_request_context()
    assert ctx_updated["model_version"] == "v2.0"

    clear_request_context()
    assert get_request_context() == {}


def test_secret_redaction():
    payload = {
        "GITHUB_TOKEN": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
        "db_url": "postgresql://postgres:secret_pass@localhost:5432/rip_db",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "normal_key": "safe_value",
    }

    redacted = redact_sensitive_data(payload)
    assert redacted["GITHUB_TOKEN"] == "[REDACTED]"
    assert redacted["db_url"] == "[REDACTED]"
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["normal_key"] == "safe_value"

    # Redact raw connection string inline
    raw_url = "redis://user:p%40ssword@localhost:6379/0"
    redacted_url = redact_sensitive_data(raw_url)
    assert "p%40ssword" not in redacted_url
    assert "[REDACTED]" in redacted_url


def test_json_formatter(caplog):
    formatter = JSONFormatter(service_name="rip_backend", version="1.0.0", environment="production")
    record = logging.LogRecord(
        name="rip_backend",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test execution message",
        args=(),
        exc_info=None,
    )
    record.request_id = "req_json_789"
    record.repository = "tensorflow/tensorflow"

    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert parsed["level"] == "INFO"
    assert parsed["service"] == "rip_backend"
    assert parsed["request_id"] == "req_json_789"
    assert parsed["repository"] == "tensorflow/tensorflow"
    assert parsed["message"] == "Test execution message"


@pytest.mark.asyncio
async def test_timing_decorator_and_context_manager():
    @log_execution_time(event_name="unit_test_async_func")
    async def sample_async_task():
        return "ok"

    res = await sample_async_task()
    assert res == "ok"

    with log_duration("unit_test_sync_block"):
        pass


def test_request_id_telemetry_and_exception_context(caplog):
    app = FastAPI()
    app.add_middleware(TelemetryMiddleware)
    register_exception_handlers(app)

    @app.get("/test-endpoint")
    async def sample_endpoint(repo: str = "unknown"):
        if repo == "fail":
            raise PredictionError("Inference failed", details={"repository": "facebook/react", "model_version": "v1.0"})
        return {"status": "ok"}

    client = TestClient(app)

    # Test successful request with request_id propagation header
    caplog.clear()
    res = client.get("/test-endpoint", headers={"X-Request-ID": "custom-req-007"})
    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == "custom-req-007"
    assert "X-Process-Time-MS" in res.headers

    # Test exception handler logs rich context
    caplog.clear()
    res_fail = client.get("/test-endpoint?repo=fail", headers={"X-Request-ID": "fail-req-999"})
    assert res_fail.status_code == 500
    data = res_fail.json()
    assert data["error_code"] == "PREDICTION_ERROR"

    # Verify exception logging captured rich context
    assert any("Exception [PREDICTION_ERROR]" in rec.message for rec in caplog.records)
    assert any(getattr(rec, "request_id", None) == "fail-req-999" for rec in caplog.records)
