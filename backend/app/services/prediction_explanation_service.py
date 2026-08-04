"""Prediction Explanation Service implementing business rules for model explainability data."""

from __future__ import annotations

from typing import Any

from backend.app.database.models.explanation import PredictionExplanation
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.logging import logger
from backend.app.services.exceptions import (
    PredictionExplanationAlreadyExists,
    PredictionExplanationNotFound,
    PredictionNotFound,
)


class PredictionExplanationService:
    """Service layer enforcing business rules for prediction explainability metadata."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize PredictionExplanationService with optional injected UnitOfWork context."""
        self.uow = uow

    async def _ensure_prediction_exists(
        self,
        uow: UnitOfWork,
        prediction_id: int,
    ) -> None:
        """Validate that referenced prediction exists in database."""
        if not await uow.predictions.exists(prediction_id):
            raise PredictionNotFound(prediction_id)

    async def _ensure_explanation_not_exists(
        self,
        uow: UnitOfWork,
        prediction_id: int,
    ) -> None:
        """Validate that no explanation already exists for prediction."""
        if await uow.explanations.exists_for_prediction(prediction_id):
            raise PredictionExplanationAlreadyExists(prediction_id)

    async def create_explanation(
        self,
        *,
        prediction_id: int,
        summary: str = "Prediction explanation",
        top_positive_features: dict[str, Any] | None = None,
        top_negative_features: dict[str, Any] | None = None,
        shap_json: dict[str, Any] | None = None,
    ) -> PredictionExplanation:
        """Create a new explanation attached to a prediction."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_prediction_exists(uow, prediction_id)
            await self._ensure_explanation_not_exists(uow, prediction_id)

            explanation = await uow.explanations.create(
                prediction_id=prediction_id,
                summary=summary,
                top_positive_features=top_positive_features or {},
                top_negative_features=top_negative_features or {},
                shap_json=shap_json or {},
            )
            await uow.commit()
            logger.info(
                "Prediction explanation created",
                extra={"prediction_id": prediction_id, "explanation_id": explanation.id},
            )
            return explanation

    async def get_explanation(
        self,
        explanation_id: int,
    ) -> PredictionExplanation:
        """Retrieve a specific prediction explanation entity by ID."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            explanation = await uow.explanations.get_by_id(explanation_id)
            if explanation is None:
                raise PredictionExplanationNotFound(explanation_id)

            logger.info(
                "Prediction explanation fetched",
                extra={"explanation_id": explanation_id},
            )
            return explanation

    async def get_by_prediction(
        self,
        prediction_id: int,
    ) -> PredictionExplanation:
        """Retrieve explanation associated with a specific prediction."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_prediction_exists(uow, prediction_id)

            explanation = await uow.explanations.get_by_prediction(prediction_id)
            if explanation is None:
                raise PredictionExplanationNotFound(prediction_id)

            logger.info(
                "Prediction explanation fetched by prediction",
                extra={"prediction_id": prediction_id},
            )
            return explanation

    async def update_explanation(
        self,
        explanation_id: int,
        **attributes: Any,
    ) -> PredictionExplanation:
        """Update an existing prediction explanation entity."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            updated = await uow.explanations.update(explanation_id, attributes)
            if updated is None:
                raise PredictionExplanationNotFound(explanation_id)

            await uow.commit()
            logger.info(
                "Prediction explanation updated",
                extra={"explanation_id": explanation_id},
            )
            return updated

    async def delete_explanation(
        self,
        explanation_id: int,
    ) -> bool:
        """Delete a prediction explanation entity."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            deleted = await uow.explanations.delete(explanation_id)
            if not deleted:
                raise PredictionExplanationNotFound(explanation_id)

            await uow.commit()
            logger.info(
                "Prediction explanation deleted",
                extra={"explanation_id": explanation_id},
            )
            return True
