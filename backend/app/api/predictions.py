"""Prediction API endpoints for Repository Intelligence Platform."""

from fastapi import APIRouter, Depends, status

from backend.app.api.deps import get_prediction_service
from backend.app.schemas import (
    PredictionCreate,
    PredictionResponse,
    PredictionUpdate,
)
from backend.app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post(
    "",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new prediction",
)
async def create_prediction(
    payload: PredictionCreate,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Record a model prediction for a repository snapshot."""
    prediction = await service.create_prediction(
        repository_snapshot_id=payload.repository_snapshot_id,
        model_version_id=payload.model_version_id,
        predicted_growth=payload.predicted_growth,
        confidence=payload.confidence,
        prediction_horizon_days=payload.prediction_horizon_days,
        prediction_timestamp=payload.prediction_timestamp,
    )
    return PredictionResponse.model_validate(prediction)


@router.get(
    "/{prediction_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get prediction by ID",
)
async def get_prediction(
    prediction_id: int,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Retrieve a prediction entity by its primary key ID."""
    prediction = await service.get_prediction(prediction_id)
    return PredictionResponse.model_validate(prediction)


@router.patch(
    "/{prediction_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update prediction attributes",
)
async def update_prediction(
    prediction_id: int,
    payload: PredictionUpdate,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Update non-null attributes of an existing prediction."""
    update_data = payload.model_dump(exclude_unset=True)
    prediction = await service.update_prediction(prediction_id, **update_data)
    return PredictionResponse.model_validate(prediction)


@router.delete(
    "/{prediction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a prediction",
)
async def delete_prediction(
    prediction_id: int,
    service: PredictionService = Depends(get_prediction_service),
) -> None:
    """Delete a prediction entity by ID."""
    await service.delete_prediction(prediction_id)


@router.get(
    "/snapshot/{snapshot_id}",
    response_model=list[PredictionResponse],
    status_code=status.HTTP_200_OK,
    summary="List predictions for a snapshot",
)
async def snapshot_predictions(
    snapshot_id: int,
    service: PredictionService = Depends(get_prediction_service),
) -> list[PredictionResponse]:
    """Retrieve all predictions recorded for a repository snapshot."""
    predictions = await service.list_predictions_for_snapshot(snapshot_id)
    return [PredictionResponse.model_validate(p) for p in predictions]
