"""Prediction entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.prediction import Prediction
from backend.app.database.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    """Strongly typed repository for managing Prediction entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PredictionRepository with session and Prediction model."""
        super().__init__(session, Prediction)

    async def latest_prediction(self, repository_snapshot_id: int) -> Prediction | None:
        """Retrieve the most recent prediction generated for a specific repository snapshot."""
        statement = (
            select(Prediction)
            .where(Prediction.repository_snapshot_id == repository_snapshot_id)
            .order_by(Prediction.prediction_timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_predictions(
        self,
        repository_snapshot_id: int | None = None,
        model_version_id: int | None = None,
    ) -> list[Prediction]:
        """Retrieve predictions with optional filtering on repository_snapshot_id or model_version_id."""
        statement = select(Prediction)
        if repository_snapshot_id is not None:
            statement = statement.where(Prediction.repository_snapshot_id == repository_snapshot_id)
        if model_version_id is not None:
            statement = statement.where(Prediction.model_version_id == model_version_id)

        statement = statement.order_by(Prediction.prediction_timestamp.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def latest_by_model(self, model_version_id: int, limit: int = 50) -> list[Prediction]:
        """Retrieve recent predictions produced by a specific ML model version."""
        statement = (
            select(Prediction)
            .where(Prediction.model_version_id == model_version_id)
            .order_by(Prediction.prediction_timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def prediction_history(self, repository_snapshot_id: int) -> list[Prediction]:
        """Retrieve complete prediction history for a repository snapshot."""
        statement = (
            select(Prediction)
            .where(Prediction.repository_snapshot_id == repository_snapshot_id)
            .order_by(Prediction.prediction_timestamp.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
