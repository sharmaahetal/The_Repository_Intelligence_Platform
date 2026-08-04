"""Snapshot Service implementing business rules for repository snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.services.exceptions import (
    DuplicateSnapshotError,
    RepositoryNotFound,
    SnapshotNotFound,
)
from backend.app.snapshots.snapshot_service import (
    RepositorySnapshotService as CollectorSnapshotService,
)


class SnapshotService:
    """Service layer enforcing domain rules for repository snapshots."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize SnapshotService with optional UnitOfWork."""
        self.uow = uow

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
        async with UnitOfWork() as uow:
            if not await uow.repositories.exists(repository_id):
                raise RepositoryNotFound(f"Repository ID {repository_id} not found.")

            existing = await uow.snapshots.get_snapshot_at(repository_id, snapshot_time)
            if existing is not None:
                raise DuplicateSnapshotError(
                    f"Snapshot for repository {repository_id} at {snapshot_time} already exists."
                )

            return await uow.snapshots.create(
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

    async def get_latest_snapshot(self, repository_id: int) -> RepositorySnapshot:
        """Retrieve the newest snapshot for a given repository."""
        async with UnitOfWork() as uow:
            if not await uow.repositories.exists(repository_id):
                raise RepositoryNotFound(f"Repository ID {repository_id} not found.")

            snapshot = await uow.snapshots.get_latest_snapshot(repository_id)
            if snapshot is None:
                raise SnapshotNotFound(f"No snapshots found for repository ID {repository_id}.")
            return snapshot

    async def list_history(self, repository_id: int) -> list[RepositorySnapshot]:
        """Return chronological snapshot history for a repository."""
        async with UnitOfWork() as uow:
            if not await uow.repositories.exists(repository_id):
                raise RepositoryNotFound(f"Repository ID {repository_id} not found.")

            return await uow.snapshots.list_repository_history(repository_id)

    async def delete_history_before(self, repository_id: int, before: datetime) -> int:
        """Purge snapshot history older than a specified datetime threshold."""
        async with UnitOfWork() as uow:
            if not await uow.repositories.exists(repository_id):
                raise RepositoryNotFound(f"Repository ID {repository_id} not found.")

            return await uow.snapshots.delete_before(before)


# Re-export Collector SnapshotService as RepositorySnapshotService for pipeline backwards compatibility
RepositorySnapshotService = CollectorSnapshotService

__all__ = [
    "SnapshotService",
    "RepositorySnapshotService",
]
