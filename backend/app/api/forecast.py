from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_forecast_service
from backend.app.api.models import ForecastResponse
from backend.app.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get("/{owner}/{repo}", response_model=ForecastResponse)
async def get_repository_forecast(
    owner: str,
    repo: str,
    horizon: int = Query(default=180, description="Forecast horizon in days (90, 180, 365)"),
    model_version: str = Query(default="v1.0", description="Model version string"),
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> ForecastResponse:
    """Thin API route delegating repository forecast generation directly to ForecastService."""
    return await forecast_service.get_forecast(
        owner=owner,
        repo=repo,
        horizon=horizon,
        model_version=model_version,
    )
