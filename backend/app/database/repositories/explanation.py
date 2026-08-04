"""PredictionExplanation entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.explanation import PredictionExplanation
from backend.app.database.repositories.base import BaseRepository


class PredictionExplanationRepository(BaseRepository[PredictionExplanation]):
    """Repository-specific data access for prediction explanation entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PredictionExplanationRepository."""
        super().__init__(session, PredictionExplanation)

    async def get_by_prediction(
        self,
        prediction_id: int,
    ) -> PredictionExplanation | None:
        """Return explanation for a prediction."""
        stmt = (
            select(PredictionExplanation)
            .where(
                PredictionExplanation.prediction_id == prediction_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_prediction(
        self,
        prediction_id: int,
    ) -> PredictionExplanation | None:
        """Alias for get_by_prediction."""
        return await self.get_by_prediction(prediction_id)

    async def exists_for_prediction(
        self,
        prediction_id: int,
    ) -> bool:
        """Return True if explanation already exists for prediction_id."""
        explanation = await self.get_by_prediction(prediction_id)
        return explanation is not None

    async def latest(self) -> PredictionExplanation | None:
        """Return newest explanation ordered by generated_at descending."""
        stmt = (
            select(PredictionExplanation)
            .order_by(
                PredictionExplanation.generated_at.desc(),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[PredictionExplanation]:
        """Return every explanation ordered newest first."""
        stmt = (
            select(PredictionExplanation)
            .order_by(
                PredictionExplanation.generated_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_prediction(
        self,
        prediction_id: int,
    ) -> bool:
        """Delete explanation attached to a prediction."""
        stmt = (
            delete(PredictionExplanation)
            .where(
                PredictionExplanation.prediction_id == prediction_id,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return (getattr(result, "rowcount", 0) or 0) > 0

    async def delete_for_prediction(
        self,
        prediction_id: int,
    ) -> bool:
        """Alias for delete_by_prediction."""
        return await self.delete_by_prediction(prediction_id)
