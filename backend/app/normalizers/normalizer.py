from dataclasses import dataclass
from datetime import datetime

from backend.app.logging import logger
from backend.app.models.snapshot import RepositorySnapshot


@dataclass
class NormalizedRepositoryData:
    """Clean, relational schema representation of a repository snapshot."""

    owner: str
    name: str
    full_name: str
    stars_count: int
    forks_count: int
    open_issues_count: int
    subscribers_count: int
    size_kb: int
    primary_language: str
    default_branch: str
    has_wiki: bool
    has_pages: bool
    snapshot_timestamp: str
    pushed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class SnapshotNormalizer:
    """Engine for normalizing RepositorySnapshot model instances into typed dataclasses."""

    def normalize(self, snapshot: RepositorySnapshot) -> NormalizedRepositoryData:
        """Normalizes RepositorySnapshot into NormalizedRepositoryData."""
        if not isinstance(snapshot, RepositorySnapshot):
            raise TypeError(f"normalize expects RepositorySnapshot, got {type(snapshot)}")

        timestamp_str = (
            snapshot.snapshot_timestamp.isoformat()
            if isinstance(snapshot.snapshot_timestamp, datetime)
            else str(snapshot.snapshot_timestamp)
        )
        pushed_str = snapshot.pushed_at.isoformat() if isinstance(snapshot.pushed_at, datetime) else snapshot.pushed_at
        created_str = snapshot.created_at.isoformat() if isinstance(snapshot.created_at, datetime) else snapshot.created_at
        updated_str = snapshot.updated_at.isoformat() if isinstance(snapshot.updated_at, datetime) else snapshot.updated_at

        data = NormalizedRepositoryData(
            owner=snapshot.owner,
            name=snapshot.name,
            full_name=snapshot.full_name,
            stars_count=snapshot.stars_count,
            forks_count=snapshot.forks_count,
            open_issues_count=snapshot.open_issues_count,
            subscribers_count=snapshot.subscribers_count,
            size_kb=snapshot.size_kb,
            primary_language=snapshot.primary_language,
            default_branch=snapshot.default_branch,
            has_wiki=snapshot.has_wiki,
            has_pages=snapshot.has_pages,
            snapshot_timestamp=timestamp_str,
            pushed_at=pushed_str,
            created_at=created_str,
            updated_at=updated_str,
        )

        logger.info("Normalized repository snapshot", extra={"full_name": data.full_name})
        return data
