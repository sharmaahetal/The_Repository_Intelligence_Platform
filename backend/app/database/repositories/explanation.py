"""PredictionExplanation entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.explanation import PredictionExplanation
from backend.app.database.repositories.base import BaseRepository


class PredictionExplanationRepository(BaseRepository[PredictionExplanation]):
    """Strongly typed repository for managing PredictionExplanation entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PredictionExplanationRepository with session and PredictionExplanation model."""
        super().__init__(session, PredictionExplanation)

    async def get_for_prediction(self, prediction_id: int) -> PredictionExplanation | None:
        """Retrieve SHAP prediction explanation associated with a specific prediction_id."""
        statement = select(PredictionExplanation).where(PredictionExplanation.prediction_id == prediction_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def delete_for_prediction(self, prediction_id: int) -> bool:
        """Delete explanation record associated with a prediction_id."""
        statement = delete(PredictionExplanation).where(PredictionExplanation.prediction_id == prediction_id)
        result = await self.session.execute(statement)
        await self.session.flush()
        return (getattr(result, "rowcount", 0) or 0) > 0

    async def exists_for_prediction(self, prediction_id: int) -> bool:
        """Check if an explanation record exists for a given prediction_id."""
        statement = select(exists().where(PredictionExplanation.prediction_id == prediction_id))
        result = await self.session.execute(statement)
        return bool(result.scalar())
