"""Prediction explanation API endpoints for Repository Intelligence Platform."""

from fastapi import APIRouter, Depends, status

from backend.app.api.deps import get_prediction_explanation_service
from backend.app.schemas import (
    PredictionExplanationCreate,
    PredictionExplanationResponse,
    PredictionExplanationUpdate,
)
from backend.app.services.prediction_explanation_service import PredictionExplanationService

router = APIRouter(prefix="/explanations", tags=["Explanations"])


@router.post(
    "",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a prediction explanation",
)
async def create_explanation(
    payload: PredictionExplanationCreate,
    service: PredictionExplanationService = Depends(get_prediction_explanation_service),
) -> PredictionExplanationResponse:
    """Create a SHAP explainability metadata record for a prediction."""
    explanation = await service.create_explanation(
        prediction_id=payload.prediction_id,
        summary=payload.summary,
        top_positive_features=payload.top_positive_features,
        top_negative_features=payload.top_negative_features,
        shap_json=payload.shap_json,
    )
    return PredictionExplanationResponse.model_validate(explanation)


@router.get(
    "/prediction/{prediction_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get explanation by prediction ID",
)
async def get_explanation_by_prediction(
    prediction_id: int,
    service: PredictionExplanationService = Depends(get_prediction_explanation_service),
) -> PredictionExplanationResponse:
    """Retrieve explanation attached to a specific prediction ID."""
    explanation = await service.get_by_prediction(prediction_id)
    return PredictionExplanationResponse.model_validate(explanation)


@router.get(
    "/{explanation_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get explanation by ID",
)
async def get_explanation(
    explanation_id: int,
    service: PredictionExplanationService = Depends(get_prediction_explanation_service),
) -> PredictionExplanationResponse:
    """Retrieve a prediction explanation entity by its primary key ID."""
    explanation = await service.get_explanation(explanation_id)
    return PredictionExplanationResponse.model_validate(explanation)


@router.patch(
    "/{explanation_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update explanation attributes",
)
async def update_explanation(
    explanation_id: int,
    payload: PredictionExplanationUpdate,
    service: PredictionExplanationService = Depends(get_prediction_explanation_service),
) -> PredictionExplanationResponse:
    """Update non-null attributes of an existing explanation."""
    update_data = payload.model_dump(exclude_unset=True)
    explanation = await service.update_explanation(explanation_id, **update_data)
    return PredictionExplanationResponse.model_validate(explanation)


@router.delete(
    "/{explanation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an explanation",
)
async def delete_explanation(
    explanation_id: int,
    service: PredictionExplanationService = Depends(get_prediction_explanation_service),
) -> None:
    """Delete a prediction explanation entity by ID."""
    await service.delete_explanation(explanation_id)
