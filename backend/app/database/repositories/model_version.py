"""ModelVersion entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.model_version import ModelVersion
from backend.app.database.repositories.base import BaseRepository


class ModelVersionRepository(BaseRepository[ModelVersion]):
    """Repository-specific data access for trained model versions."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ModelVersionRepository."""
        super().__init__(session, ModelVersion)

    async def get_by_version(
        self,
        version: str,
    ) -> ModelVersion | None:
        """Retrieve a model version entity by semantic version string."""
        stmt = (
            select(ModelVersion)
            .where(
                ModelVersion.version == version,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_version(
        self,
        version: str,
    ) -> bool:
        """Check if a model version string exists."""
        model = await self.get_by_version(version)
        return model is not None

    async def latest_version(self) -> ModelVersion | None:
        """Return the newest trained model version."""
        stmt = (
            select(ModelVersion)
            .order_by(
                ModelVersion.trained_at.desc(),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_versions(self) -> list[ModelVersion]:
        """Return every model version sorted newest first."""
        stmt = (
            select(ModelVersion)
            .order_by(
                ModelVersion.trained_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def best_model(
        self,
        metric: str = "f1",
    ) -> ModelVersion | None:
        """Retrieve model version possessing highest metric value."""
        allowed_metrics = {
            "accuracy",
            "precision",
            "recall",
            "f1",
            "auc",
        }

        if metric not in allowed_metrics:
            raise ValueError(f"Unsupported metric: {metric}")

        metric_column = getattr(ModelVersion, metric)
        stmt = (
            select(ModelVersion)
            .order_by(
                desc(metric_column),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
