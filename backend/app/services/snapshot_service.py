"""Snapshot service module re-exporting SnapshotService."""

from backend.app.snapshots.snapshot_service import (
    RepositorySnapshotService,
    SnapshotService,
)

__all__ = ["SnapshotService", "RepositorySnapshotService"]
