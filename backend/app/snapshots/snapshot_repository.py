from datetime import UTC, datetime

from backend.app.logging import logger
from backend.app.models.snapshot import RepositorySnapshot


class SnapshotRepository:
    """Data Access Layer for persisting and retrieving RepositorySnapshot domain entities.

    Stores strictly RepositorySnapshot models. Contains no business or collection logic.
    """

    def __init__(self) -> None:
        self._snapshots: list[RepositorySnapshot] = []

    async def save_snapshot(self, snapshot: RepositorySnapshot) -> None:
        """Persist RepositorySnapshot domain entity."""
        if not isinstance(snapshot, RepositorySnapshot):
            raise TypeError(
                f"SnapshotRepository requires RepositorySnapshot instance, got {type(snapshot)}"
            )

        self._snapshots.append(snapshot)
        logger.info(
            "Persisted RepositorySnapshot entity in snapshot storage",
            extra={
                "owner": snapshot.owner,
                "repo": snapshot.name,
                "snapshot_time": snapshot.snapshot_time.isoformat(),
                "schema_version": snapshot.schema_version,
            },
        )

    async def get_latest_snapshot(self, owner: str, repo: str) -> RepositorySnapshot | None:
        """Retrieve the most recent RepositorySnapshot for a repository."""
        matches = [
            s
            for s in self._snapshots
            if s.owner.lower() == owner.lower() and s.name.lower() == repo.lower()
        ]
        if not matches:
            return None
        return max(matches, key=lambda s: s.snapshot_time)

    async def get_snapshot_at_time(
        self, owner: str, repo: str, snapshot_time: datetime
    ) -> RepositorySnapshot | None:
        """Retrieve the RepositorySnapshot matching specific timestamp, or None if not found."""
        target_utc = snapshot_time if snapshot_time.tzinfo else snapshot_time.replace(tzinfo=UTC)

        for snapshot in self._snapshots:
            if (
                snapshot.owner.lower() == owner.lower()
                and snapshot.name.lower() == repo.lower()
                and snapshot.snapshot_time == target_utc
            ):
                return snapshot
        return None
