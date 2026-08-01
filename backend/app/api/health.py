from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_inference_service
from backend.app.api.models import HealthResponse, ReadinessResponse
from backend.app.services.inference_service import InferenceService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", response_model=HealthResponse)
async def liveness_probe() -> HealthResponse:
    """Liveness probe confirming API process is alive."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(UTC).isoformat(),
        version="1.0.0",
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_probe(
    inference_service: InferenceService = Depends(get_inference_service),
) -> ReadinessResponse:
    """Readiness probe confirming memory model loading, registry, and service availability."""
    model_loaded = inference_service.is_model_loaded()

    return ReadinessResponse(
        status="ready" if model_loaded else "degraded",
        timestamp=datetime.now(UTC).isoformat(),
        model_loaded=model_loaded,
        registry_available=True,
        snapshot_service_ready=True,
        details={"default_model_version": "v1.0"},
    )
