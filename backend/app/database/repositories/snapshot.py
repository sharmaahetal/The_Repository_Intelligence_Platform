"""Repository snapshot entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.database.repositories.base import BaseRepository


class SnapshotRepository(BaseRepository[RepositorySnapshot]):
    """Strongly typed repository for managing RepositorySnapshot entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize SnapshotRepository with session and RepositorySnapshot model."""
        super().__init__(session, RepositorySnapshot)

    async def get_latest_snapshot(self, repository_id: int) -> RepositorySnapshot | None:
        """Retrieve the most recent point-in-time snapshot for a given repository."""
        statement = (
            select(RepositorySnapshot)
            .where(RepositorySnapshot.repository_id == repository_id)
            .order_by(RepositorySnapshot.snapshot_time.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_repository_history(
        self,
        repository_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RepositorySnapshot]:
        """Retrieve paginated historical metric snapshots for a repository sorted descending by snapshot_time."""
        statement = (
            select(RepositorySnapshot)
            .where(RepositorySnapshot.repository_id == repository_id)
            .order_by(RepositorySnapshot.snapshot_time.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete_before(self, cutoff_time: datetime) -> int:
        """Delete all repository snapshots older than the specified cutoff timestamp."""
        statement = (
            delete(RepositorySnapshot)
            .where(RepositorySnapshot.snapshot_time < cutoff_time)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(statement)
        await self.session.flush()
        return getattr(result, "rowcount", 0) or 0

    async def get_snapshot_at(self, repository_id: int, target_time: datetime) -> RepositorySnapshot | None:
        """Retrieve the closest snapshot for a repository occurring on or prior to target_time."""
        statement = (
            select(RepositorySnapshot)
            .where(
                RepositorySnapshot.repository_id == repository_id,
                RepositorySnapshot.snapshot_time <= target_time,
            )
            .order_by(RepositorySnapshot.snapshot_time.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def count_snapshots(self, repository_id: int) -> int:
        """Count total snapshot instances recorded for a specific repository."""
        statement = (
            select(func.count(1))
            .select_from(RepositorySnapshot)
            .where(RepositorySnapshot.repository_id == repository_id)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() or 0
