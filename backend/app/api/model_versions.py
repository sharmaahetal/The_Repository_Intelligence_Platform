"""Model version API endpoints for Repository Intelligence Platform."""

from fastapi import APIRouter, Depends, Query, status

from backend.app.api.deps import get_model_version_service
from backend.app.schemas import (
    ModelVersionCreate,
    ModelVersionResponse,
    ModelVersionUpdate,
)
from backend.app.services.model_version_service import ModelVersionService

router = APIRouter(prefix="/model-versions", tags=["Model Versions"])


@router.post(
    "",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new model version",
)
async def register_model(
    payload: ModelVersionCreate,
    service: ModelVersionService = Depends(get_model_version_service),
) -> ModelVersionResponse:
    """Register a new trained ML model version into the registry."""
    model = await service.register_model(
        version=payload.version,
        algorithm=payload.algorithm,
        training_dataset_hash=payload.training_dataset_hash,
        feature_schema_version=payload.feature_schema_version,
        accuracy=payload.accuracy,
        precision=payload.precision,
        recall=payload.recall,
        f1=payload.f1,
        auc=payload.auc,
        artifact_path=payload.artifact_path,
        trained_at=payload.trained_at,
        training_duration_seconds=payload.training_duration_seconds,
        cross_validation_score=payload.cross_validation_score,
        dataset_size=payload.dataset_size,
        random_seed=payload.random_seed,
        git_commit_hash=payload.git_commit_hash,
    )
    return ModelVersionResponse.model_validate(model)


@router.get(
    "",
    response_model=list[ModelVersionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all model versions",
)
async def list_models(
    service: ModelVersionService = Depends(get_model_version_service),
) -> list[ModelVersionResponse]:
    """Retrieve all registered model versions sorted newest first."""
    models = await service.list_models()
    return [ModelVersionResponse.model_validate(m) for m in models]


@router.get(
    "/latest",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get latest model version",
)
async def get_latest_model(
    service: ModelVersionService = Depends(get_model_version_service),
) -> ModelVersionResponse:
    """Retrieve the most recently registered model version."""
    model = await service.latest_model()
    return ModelVersionResponse.model_validate(model)


@router.get(
    "/best",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get best performing model version",
)
async def get_best_model(
    metric: str = Query("f1", description="Evaluation metric to sort by (f1, accuracy, auc)"),
    service: ModelVersionService = Depends(get_model_version_service),
) -> ModelVersionResponse:
    """Retrieve the model version possessing the highest metric score."""
    model = await service.best_model(metric=metric)
    return ModelVersionResponse.model_validate(model)


@router.get(
    "/{model_id}",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get model version by ID",
)
async def get_model(
    model_id: int,
    service: ModelVersionService = Depends(get_model_version_service),
) -> ModelVersionResponse:
    """Retrieve a specific model version entity by its primary key ID."""
    model = await service.get_model(model_id=model_id)
    return ModelVersionResponse.model_validate(model)


@router.patch(
    "/{model_id}",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update model version attributes",
)
async def update_model(
    model_id: int,
    payload: ModelVersionUpdate,
    service: ModelVersionService = Depends(get_model_version_service),
) -> ModelVersionResponse:
    """Update non-null attributes of an existing model version."""
    update_data = payload.model_dump(exclude_unset=True)
    model = await service.update_model(model_id, **update_data)
    return ModelVersionResponse.model_validate(model)


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a model version",
)
async def delete_model(
    model_id: int,
    service: ModelVersionService = Depends(get_model_version_service),
) -> None:
    """Delete a model version entity by ID from the registry."""
    await service.delete_model(model_id)
