"""Repository snapshot entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.database.repositories.base import BaseRepository


class SnapshotRepository(BaseRepository[RepositorySnapshot]):
    """Repository-specific data access for repository snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize SnapshotRepository with session and RepositorySnapshot model."""
        super().__init__(session, RepositorySnapshot)

    async def get_latest_snapshot(
        self,
        repository_id: int,
    ) -> RepositorySnapshot | None:
        """Given a repository ID, return its newest snapshot."""
        stmt = (
            select(RepositorySnapshot)
            .where(
                RepositorySnapshot.repository_id == repository_id,
            )
            .order_by(
                RepositorySnapshot.snapshot_time.desc(),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_repository_history(
        self,
        repository_id: int,
    ) -> list[RepositorySnapshot]:
        """Return every snapshot for one repository in ascending chronological order."""
        stmt = (
            select(RepositorySnapshot)
            .where(
                RepositorySnapshot.repository_id == repository_id,
            )
            .order_by(
                RepositorySnapshot.snapshot_time.asc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_snapshot_at(
        self,
        repository_id: int,
        snapshot_time: datetime,
    ) -> RepositorySnapshot | None:
        """Return snapshot captured for a repository at a specific timestamp."""
        stmt = select(RepositorySnapshot).where(
            RepositorySnapshot.repository_id == repository_id,
            RepositorySnapshot.snapshot_time == snapshot_time,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_snapshots(
        self,
        repository_id: int,
    ) -> int:
        """Return the number of snapshots for a repository."""
        stmt = (
            select(func.count(RepositorySnapshot.id))
            .select_from(RepositorySnapshot)
            .where(
                RepositorySnapshot.repository_id == repository_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or 0

    async def delete_before(
        self,
        before: datetime,
    ) -> int:
        """Delete all snapshots older than the given timestamp."""
        stmt = delete(RepositorySnapshot).where(
            RepositorySnapshot.snapshot_time < before,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return getattr(result, "rowcount", 0) or 0
