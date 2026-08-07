"""Snapshot Service implementing business rules for repository snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.logging import logger
from backend.app.services.exceptions import (
    DuplicateSnapshotError,
    RepositoryNotFound,
    SnapshotNotFound,
)
from backend.app.snapshots.snapshot_service import (
    RepositorySnapshotService as CollectorSnapshotService,
)


class SnapshotService:
    """Service layer enforcing domain rules for time-series repository snapshots."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize SnapshotService with optional injected UnitOfWork context."""
        self.uow = uow

    async def _ensure_repository_exists(
        self,
        uow: UnitOfWork,
        repository_id: int,
    ) -> None:
        """Validate that target repository exists in database."""
        if not await uow.repositories.exists(repository_id):
            raise RepositoryNotFound(repository_id)

    async def _ensure_snapshot_not_exists(
        self,
        uow: UnitOfWork,
        repository_id: int,
        snapshot_time: datetime,
    ) -> None:
        """Validate that no snapshot exists at identical timestamp for repository."""
        existing = await uow.snapshots.get_snapshot_at(repository_id, snapshot_time)
        if existing is not None:
            raise DuplicateSnapshotError(repository_id, snapshot_time)

    async def create_snapshot(
        self,
        repository_id: int,
        snapshot_time: datetime,
        stars: int = 0,
        forks: int = 0,
        open_issues: int = 0,
        watchers: int = 0,
        subscribers: int = 0,
        network_count: int = 0,
        size_kb: int = 0,
        license: str | None = None,  # noqa: A002
        topics_json: dict[str, Any] | list[str] | None = None,
        default_branch: str = "main",
    ) -> RepositorySnapshot:
        """Record a new point-in-time repository snapshot."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_repository_exists(uow, repository_id)
            await self._ensure_snapshot_not_exists(uow, repository_id, snapshot_time)

            snapshot = await uow.snapshots.create(
                repository_id=repository_id,
                snapshot_time=snapshot_time,
                stars=stars,
                forks=forks,
                open_issues=open_issues,
                watchers=watchers,
                subscribers=subscribers,
                network_count=network_count,
                size_kb=size_kb,
                license=license,
                topics_json=topics_json,
                default_branch=default_branch,
            )
            await uow.commit()
            logger.info(
                "Snapshot created",
                extra={"repository_id": repository_id, "snapshot_time": snapshot_time},
            )
            return snapshot

    async def get_snapshot_by_id(self, snapshot_id: int) -> RepositorySnapshot:
        """Retrieve a snapshot entity by its primary key ID."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            snapshot = await uow.snapshots.get_by_id(snapshot_id)
            if snapshot is None:
                raise SnapshotNotFound(snapshot_id)
            return snapshot

    async def update_snapshot(
        self,
        snapshot_id: int,
        **attributes: Any,
    ) -> RepositorySnapshot:
        """Update attributes of an existing snapshot entity."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            updated = await uow.snapshots.update(snapshot_id, attributes)
            if updated is None:
                raise SnapshotNotFound(snapshot_id)
            await uow.commit()
            logger.info("Snapshot updated", extra={"snapshot_id": snapshot_id})
            return updated

    async def delete_snapshot(self, snapshot_id: int) -> bool:
        """Delete a snapshot entity by its primary key ID."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            deleted = await uow.snapshots.delete(snapshot_id)
            if not deleted:
                raise SnapshotNotFound(snapshot_id)
            await uow.commit()
            logger.info("Snapshot deleted", extra={"snapshot_id": snapshot_id})
            return True

    async def latest_snapshot(self, repository_id: int) -> RepositorySnapshot:
        """Retrieve the newest snapshot for a given repository."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_repository_exists(uow, repository_id)

            snapshot = await uow.snapshots.get_latest_snapshot(repository_id)
            if snapshot is None:
                raise SnapshotNotFound(repository_id)

            logger.info("Latest snapshot requested", extra={"repository_id": repository_id})
            return snapshot

    async def get_latest_snapshot(self, repository_id: int) -> RepositorySnapshot:
        """Alias for latest_snapshot."""
        return await self.latest_snapshot(repository_id)

    async def snapshot_history(self, repository_id: int) -> list[RepositorySnapshot]:
        """Return chronological snapshot history for a repository."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_repository_exists(uow, repository_id)

            history = await uow.snapshots.list_repository_history(repository_id)
            logger.info("Snapshot history requested", extra={"repository_id": repository_id})
            return history

    async def list_history(self, repository_id: int) -> list[RepositorySnapshot]:
        """Alias for snapshot_history."""
        return await self.snapshot_history(repository_id)

    async def get_snapshot(
        self,
        repository_id: int,
        snapshot_time: datetime,
    ) -> RepositorySnapshot:
        """Retrieve a specific snapshot by repository ID and timestamp."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            await self._ensure_repository_exists(uow, repository_id)

            snapshot = await uow.snapshots.get_snapshot_at(repository_id, snapshot_time)
            if snapshot is None:
                raise SnapshotNotFound(repository_id)
            return snapshot

    async def delete_old_snapshots(
        self,
        before: datetime,
        repository_id: int | None = None,
    ) -> int:
        """Purge snapshot history older than a specified datetime threshold."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            if repository_id is not None:
                await self._ensure_repository_exists(uow, repository_id)

            deleted_count = await uow.snapshots.delete_before(before)
            await uow.commit()
            logger.info(
                "Old snapshots deleted",
                extra={"before": before, "deleted_count": deleted_count},
            )
            return deleted_count

    async def delete_history_before(self, repository_id: int, before: datetime) -> int:
        """Alias for delete_old_snapshots."""
        return await self.delete_old_snapshots(before, repository_id=repository_id)


# Re-export Collector SnapshotService as RepositorySnapshotService for pipeline backwards compatibility
RepositorySnapshotService = CollectorSnapshotService

__all__ = [
    "SnapshotService",
    "RepositorySnapshotService",
]
