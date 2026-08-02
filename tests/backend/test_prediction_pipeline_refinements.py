from datetime import UTC, datetime
from unittest.mock import AsyncMock
import pytest

from backend.app.api.exceptions import ErrorBody, ErrorResponse
from backend.app.api.models import ForecastDetails, ForecastResponse
from backend.app.models.context import PredictionContext
from backend.app.models.snapshot import RepositorySnapshot
from backend.app.services.prediction_pipeline import PredictionCache, PredictionPipeline


def test_prediction_context_instantiation():
    ctx = PredictionContext(
        owner="tensorflow",
        repo="tensorflow",
        horizon=90,
        model_version="v2.0",
    )

    assert ctx.owner == "tensorflow"
    assert ctx.repo == "tensorflow"
    assert ctx.horizon == 90
    assert ctx.model_version == "v2.0"
    assert ctx.request_id.startswith("req_")
    assert ctx.feature_schema_version == 1


def test_prediction_cache_idempotency():
    cache = PredictionCache(ttl_seconds=300)
    h1 = cache.compute_hash("pytorch", "pytorch", 180, "v1.0")
    h2 = cache.compute_hash("PyTorch", "PyTorch", 180, "v1.0")

    # Lowercase case-insensitivity
    assert h1 == h2

    dummy_response = ForecastResponse(
        repository="pytorch/pytorch",
        owner="pytorch",
        repo="pytorch",
        prediction_horizon_days=180,
        snapshot_time=datetime.now(UTC).isoformat(),
        forecast=ForecastDetails(
            growth_probability=0.90,
            abandonment_probability=0.05,
            maintainer_retention_probability=0.95,
            derived_health_index=92,
        ),
        confidence=0.94,
        narrative_summary="High growth trajectory",
        cached=False,
    )

    cache.set(h1, dummy_response)

    res = cache.get(h1)
    assert res is not None
    assert res.owner == "pytorch"


def test_standardized_error_response_format():
    err_resp = ErrorResponse(
        error_code="MODEL_NOT_FOUND",
        message="Model artifact not found",
        request_id="req-12345",
    )

    assert err_resp.error.code == "MODEL_NOT_FOUND"
    assert err_resp.error.message == "Model artifact not found"
    assert err_resp.error.request_id == "req-12345"

    d = err_resp.model_dump()
    assert "error" in d
    assert d["error"]["code"] == "MODEL_NOT_FOUND"
    assert d["error"]["message"] == "Model artifact not found"
    assert d["error"]["request_id"] == "req-12345"
    assert "timestamp" in d["error"]


@pytest.mark.asyncio
async def test_prediction_pipeline_end_to_end_idempotency():
    mock_snapshot = RepositorySnapshot(
        repository_id=123,
        owner="pallets",
        name="flask",
        stars=65000,
        forks=15000,
        snapshot_time=datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC),
    )

    mock_snapshot_service = AsyncMock()
    mock_snapshot_service.get_snapshot.return_value = mock_snapshot

    pipeline = PredictionPipeline(snapshot_service=mock_snapshot_service)

    res1 = await pipeline.execute_pipeline(owner="pallets", repo="flask", horizon=180)
    assert res1.cached is False
    assert res1.prediction_id.startswith("pred_")
    assert res1.latency_ms >= 0

    # Second call should hit idempotency cache
    res2 = await pipeline.execute_pipeline(owner="pallets", repo="flask", horizon=180)
    assert res2.cached is True
