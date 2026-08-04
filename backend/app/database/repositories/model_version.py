"""ModelVersion entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.model_version import ModelVersion
from backend.app.database.repositories.base import BaseRepository


class ModelVersionRepository(BaseRepository[ModelVersion]):
    """Strongly typed repository for managing ModelVersion entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ModelVersionRepository with session and ModelVersion model."""
        super().__init__(session, ModelVersion)

    async def latest_version(self) -> ModelVersion | None:
        """Retrieve the most recently trained ML model version."""
        statement = select(ModelVersion).order_by(ModelVersion.trained_at.desc()).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_version(self, version: str) -> ModelVersion | None:
        """Retrieve a model version entity by semantic version string (e.g. 'v1.0.0')."""
        statement = select(ModelVersion).where(ModelVersion.version == version)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def best_model(self, metric: str = "f1") -> ModelVersion | None:
        """Retrieve model version possessing highest metric value (e.g., f1, accuracy, auc, precision, recall)."""
        valid_metrics = {"f1", "accuracy", "precision", "recall", "auc"}
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric '{metric}'. Must be one of {valid_metrics}")

        col = getattr(ModelVersion, metric)
        statement = select(ModelVersion).order_by(col.desc()).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_versions(self) -> list[ModelVersion]:
        """Retrieve all model versions sorted descending by training timestamp."""
        statement = select(ModelVersion).order_by(ModelVersion.trained_at.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())
