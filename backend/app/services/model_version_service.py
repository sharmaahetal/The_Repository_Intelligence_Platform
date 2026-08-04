"""Model Version Service managing the machine learning model registry."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.database.models.model_version import ModelVersion
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.logging import logger
from backend.app.services.exceptions import (
    ModelVersionAlreadyExists,
    ModelVersionNotFound,
)


class ModelVersionService:
    """Service layer enforcing domain rules for trained machine learning model versions."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize ModelVersionService with injected or default UnitOfWork dependency."""
        self.uow = uow or UnitOfWork()

    async def _ensure_model_exists(self, uow: UnitOfWork, model_id: int) -> None:
        """Validate that target model version exists in database."""
        if not await uow.model_versions.exists(model_id):
            raise ModelVersionNotFound(model_id)

    async def _ensure_version_unique(self, uow: UnitOfWork, version: str) -> None:
        """Validate that target version string is unique in registry."""
        if await uow.model_versions.exists_by_version(version):
            raise ModelVersionAlreadyExists(version)

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
        async with self.uow as uow:
            await self._ensure_version_unique(uow, version)

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

            model = await uow.model_versions.create(**create_kwargs)
            await uow.commit()
            logger.info("model registered", extra={"version": version, "algorithm": algorithm})
            return model

    async def get_model(
        self,
        model_id: int | None = None,
        version: str | None = None,
    ) -> ModelVersion:
        """Retrieve a specific model version entity by ID or version string."""
        if model_id is None and version is None:
            raise ValueError("Either model_id or version string must be provided.")

        async with self.uow as uow:
            model: ModelVersion | None = None
            if model_id is not None:
                model = await uow.model_versions.get_by_id(model_id)
            elif version is not None:
                model = await uow.model_versions.get_by_version(version)

            if model is None:
                raise ModelVersionNotFound(model_id if model_id is not None else (version or "unknown"))
            return model

    async def get_model_by_version(self, version: str) -> ModelVersion:
        """Alias for get_model(version=...)."""
        return await self.get_model(version=version)

    async def latest_model(self) -> ModelVersion:
        """Retrieve the newest trained model version."""
        async with self.uow as uow:
            model = await uow.model_versions.latest_version()
            if model is None:
                raise ModelVersionNotFound("latest")
            logger.info("latest model requested")
            return model

    async def get_latest_model(self) -> ModelVersion:
        """Alias for latest_model."""
        return await self.latest_model()

    async def best_model(self, metric: str = "f1") -> ModelVersion:
        """Retrieve the model version possessing the highest metric score."""
        async with self.uow as uow:
            model = await uow.model_versions.best_model(metric=metric)
            if model is None:
                raise ModelVersionNotFound(f"best_{metric}")
            logger.info("best model requested", extra={"metric": metric})
            return model

    async def get_best_model(self, metric: str = "f1") -> ModelVersion:
        """Alias for best_model."""
        return await self.best_model(metric=metric)

    async def list_models(self) -> list[ModelVersion]:
        """Return all registered model versions sorted newest first."""
        async with self.uow as uow:
            return await uow.model_versions.list_versions()

    async def update_model(
        self,
        model_id: int,
        **attributes: Any,
    ) -> ModelVersion:
        """Update an existing model version entity."""
        async with self.uow as uow:
            await self._ensure_model_exists(uow, model_id)

            updated = await uow.model_versions.update(model_id, attributes)
            if updated is None:
                raise ModelVersionNotFound(model_id)

            await uow.commit()
            logger.info("model updated", extra={"model_id": model_id})
            return updated

    async def delete_model(
        self,
        model_id: int,
    ) -> bool:
        """Delete a model version entity from registry."""
        async with self.uow as uow:
            await self._ensure_model_exists(uow, model_id)

            deleted = await uow.model_versions.delete(model_id)
            await uow.commit()
            logger.info("model deleted", extra={"model_id": model_id})
            return deleted
