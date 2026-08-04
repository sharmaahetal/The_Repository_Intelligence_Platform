"""Prediction Service implementing business rules for model predictions and explanations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.database.models.prediction import Prediction
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.logging import logger
from backend.app.services.exceptions import (
    DuplicatePredictionError,
    InvalidPredictionRequest,
    ModelNotFound,
    ModelVersionNotFound,
    PredictionNotFound,
    SnapshotNotFound,
)


class PredictionService:
    """Service layer orchestrating prediction inference results and explainability metadata."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize PredictionService with optional injected UnitOfWork context."""
        self.uow = uow

    async def _ensure_snapshot_exists(
        self,
        uow: UnitOfWork,
        repository_snapshot_id: int,
    ) -> None:
        """Validate that target repository snapshot exists in database."""
        if not await uow.snapshots.exists(repository_snapshot_id):
            raise SnapshotNotFound(repository_snapshot_id)

    async def _ensure_model_exists(
        self,
        uow: UnitOfWork,
        model_version_id: int,
    ) -> None:
        """Validate that target model version exists in database."""
        if not await uow.model_versions.exists(model_version_id):
            raise ModelVersionNotFound(model_version_id)

    async def _ensure_prediction_not_exists(
        self,
        uow: UnitOfWork,
        repository_snapshot_id: int,
        model_version_id: int,
        prediction_horizon_days: int,
    ) -> None:
        """Validate that no identical prediction exists for snapshot, model version, and horizon."""
        existing = await uow.predictions.list_predictions(repository_snapshot_id)
        for p in existing:
            if (
                p.model_version_id == model_version_id
                and p.prediction_horizon_days == prediction_horizon_days
            ):
                raise DuplicatePredictionError(
                    f"snapshot={repository_snapshot_id}, model={model_version_id}, horizon={prediction_horizon_days}"
                )

    async def create_prediction(
        self,
        *,
        repository_snapshot_id: int,
        model_version_id: int,
        predicted_growth: float,
        confidence: float,
        prediction_horizon_days: int = 30,
        prediction_timestamp: datetime | None = None,
        explanation_summary: str | None = None,
        top_positive_features: dict[str, Any] | None = None,
        top_negative_features: dict[str, Any] | None = None,
        shap_json: dict[str, Any] | None = None,
    ) -> Prediction:
        """Record a model prediction and optional SHAP explanation in an atomic transaction."""
        if prediction_horizon_days <= 0:
            raise InvalidPredictionRequest("prediction_horizon_days must be greater than 0.")

        if not (0.0 <= confidence <= 1.0):
            raise InvalidPredictionRequest("confidence must be between 0.0 and 1.0.")

        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_snapshot_exists(uow, repository_snapshot_id)

            try:
                await self._ensure_model_exists(uow, model_version_id)
            except ModelVersionNotFound as err:
                raise ModelNotFound(model_version_id) from err

            await self._ensure_prediction_not_exists(
                uow,
                repository_snapshot_id,
                model_version_id,
                prediction_horizon_days,
            )

            ts = prediction_timestamp if prediction_timestamp is not None else datetime.now(UTC)

            prediction = await uow.predictions.create(
                repository_snapshot_id=repository_snapshot_id,
                model_version_id=model_version_id,
                predicted_growth=predicted_growth,
                confidence=confidence,
                prediction_horizon_days=prediction_horizon_days,
                prediction_timestamp=ts,
            )

            if explanation_summary is not None or shap_json is not None:
                await uow.explanations.create(
                    prediction_id=prediction.id,
                    summary=explanation_summary or "Prediction explanation",
                    top_positive_features=top_positive_features or {},
                    top_negative_features=top_negative_features or {},
                    shap_json=shap_json or {},
                )

            await uow.commit()
            logger.info(
                "Prediction created",
                extra={
                    "snapshot_id": repository_snapshot_id,
                    "model_version": model_version_id,
                    "confidence": confidence,
                },
            )
            return prediction

    async def get_prediction(self, prediction_id: int) -> Prediction:
        """Retrieve a specific prediction entity by ID."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            prediction = await uow.predictions.get_by_id(prediction_id)
            if prediction is None:
                raise PredictionNotFound(prediction_id)

            logger.info("Prediction fetched", extra={"prediction_id": prediction_id})
            return prediction

    async def latest_prediction(self, repository_snapshot_id: int) -> Prediction:
        """Retrieve the newest prediction recorded for a snapshot."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_snapshot_exists(uow, repository_snapshot_id)

            prediction = await uow.predictions.latest_prediction(repository_snapshot_id)
            if prediction is None:
                raise PredictionNotFound(repository_snapshot_id)

            logger.info("Latest prediction fetched", extra={"snapshot_id": repository_snapshot_id})
            return prediction

    async def get_latest_prediction(self, repository_snapshot_id: int) -> Prediction:
        """Alias for latest_prediction."""
        return await self.latest_prediction(repository_snapshot_id)

    async def list_predictions_for_snapshot(self, repository_snapshot_id: int) -> list[Prediction]:
        """Return all predictions generated for a snapshot."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_snapshot_exists(uow, repository_snapshot_id)
            return await uow.predictions.list_predictions(repository_snapshot_id)

    async def prediction_history(self, model_version_id: int) -> list[Prediction]:
        """Return prediction history generated by a specific model version."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_model_exists(uow, model_version_id)
            return await uow.predictions.prediction_history(model_version_id)

    async def get_prediction_history(self, model_version_id: int) -> list[Prediction]:
        """Alias for prediction_history."""
        return await self.prediction_history(model_version_id)

    async def high_confidence_predictions(self, minimum_confidence: float) -> list[Prediction]:
        """Return predictions meeting or exceeding the specified minimum confidence score."""
        if not (0.0 <= minimum_confidence <= 1.0):
            raise InvalidPredictionRequest("minimum_confidence must be between 0.0 and 1.0.")

        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            predictions = await uow.predictions.high_confidence_predictions(minimum_confidence)
            logger.info(
                "High-confidence search",
                extra={"minimum_confidence": minimum_confidence, "count": len(predictions)},
            )
            return predictions

    async def get_high_confidence_predictions(self, minimum_confidence: float) -> list[Prediction]:
        """Alias for high_confidence_predictions."""
        return await self.high_confidence_predictions(minimum_confidence)

    async def delete_prediction(self, prediction_id: int) -> bool:
        """Delete a prediction entity."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            prediction = await uow.predictions.get_by_id(prediction_id)
            if prediction is None:
                raise PredictionNotFound(prediction_id)

            result = await uow.predictions.delete(prediction_id)
            await uow.commit()
            logger.info("Prediction deleted", extra={"prediction_id": prediction_id})
            return result
