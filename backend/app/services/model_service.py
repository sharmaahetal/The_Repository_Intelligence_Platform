"""Model Service implementing business rules for model versions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.database.models.model_version import ModelVersion
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.services.exceptions import ModelNotFound, ServiceException


class ModelService:
    """Service layer enforcing domain rules for trained machine learning model versions."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize ModelService with optional UnitOfWork."""
        self.uow = uow

    async def register_model(
        self,
        *,
        version: str,
        algorithm: str,
        training_dataset_hash: str,
        feature_schema_version: str,
        accuracy: float,
        precision: float,
        recall: float,
        f1: float,
        auc: float,
        artifact_path: str,
        trained_at: datetime | None = None,
        training_duration_seconds: float | None = None,
        cross_validation_score: float | None = None,
        dataset_size: int | None = None,
        random_seed: int | None = None,
        git_commit_hash: str | None = None,
    ) -> ModelVersion:
        """Register a new trained model version after ensuring semantic version uniqueness."""
        async with UnitOfWork() as uow:
            if await uow.model_versions.exists_by_version(version):
                raise ServiceException(f"Model version '{version}' is already registered.")

            create_kwargs: dict[str, Any] = {
                "version": version,
                "algorithm": algorithm,
                "training_dataset_hash": training_dataset_hash,
                "feature_schema_version": feature_schema_version,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "auc": auc,
                "artifact_path": artifact_path,
                "trained_at": trained_at if trained_at is not None else datetime.now(UTC),
                "training_duration_seconds": training_duration_seconds,
                "cross_validation_score": cross_validation_score,
                "dataset_size": dataset_size,
                "random_seed": random_seed,
                "git_commit_hash": git_commit_hash,
            }

            return await uow.model_versions.create(**create_kwargs)

    async def get_latest_model(self) -> ModelVersion:
        """Retrieve the newest trained model version."""
        async with UnitOfWork() as uow:
            model = await uow.model_versions.latest_version()
            if model is None:
                raise ModelNotFound("No trained model versions are registered.")
            return model

    async def get_best_model(self, metric: str = "f1") -> ModelVersion:
        """Retrieve the model version possessing the highest metric value."""
        async with UnitOfWork() as uow:
            model = await uow.model_versions.best_model(metric=metric)
            if model is None:
                raise ModelNotFound(f"No trained model versions found to calculate best model by '{metric}'.")
            return model

    async def get_model_by_version(self, version: str) -> ModelVersion:
        """Retrieve a specific model version by semantic version string."""
        async with UnitOfWork() as uow:
            model = await uow.model_versions.get_by_version(version)
            if model is None:
                raise ModelNotFound(f"Model version '{version}' was not found.")
            return model

    async def list_models(self) -> list[ModelVersion]:
        """Return all registered model versions sorted newest first."""
        async with UnitOfWork() as uow:
            return await uow.model_versions.list_versions()
