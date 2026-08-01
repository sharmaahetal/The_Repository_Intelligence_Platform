from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.logging import logger
from app.models.snapshot import RepositorySnapshot


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
    """Engine for normalizing RepositorySnapshot models or dicts into typed dataclasses."""

    def normalize(self, snapshot: RepositorySnapshot | dict[str, Any]) -> NormalizedRepositoryData:
        """Normalizes snapshot into NormalizedRepositoryData."""
        if isinstance(snapshot, RepositorySnapshot):
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
        else:
            raw_ts = snapshot.get("snapshot_timestamp")
            if isinstance(raw_ts, datetime):
                timestamp_str = raw_ts.isoformat()
            else:
                timestamp_str = str(raw_ts) if raw_ts else datetime.now(UTC).isoformat()

            data = NormalizedRepositoryData(
                owner=snapshot.get("owner", ""),
                name=snapshot.get("name", ""),
                full_name=snapshot.get("full_name", ""),
                stars_count=int(snapshot.get("stars_count", 0)),
                forks_count=int(snapshot.get("forks_count", 0)),
                open_issues_count=int(snapshot.get("open_issues_count", 0)),
                subscribers_count=int(snapshot.get("subscribers_count", 0)),
                size_kb=int(snapshot.get("size_kb", 0)),
                primary_language=snapshot.get("primary_language", "Unknown"),
                default_branch=snapshot.get("default_branch", "main"),
                has_wiki=bool(snapshot.get("has_wiki", False)),
                has_pages=bool(snapshot.get("has_pages", False)),
                snapshot_timestamp=timestamp_str,
                pushed_at=snapshot.get("pushed_at"),
                created_at=snapshot.get("created_at"),
                updated_at=snapshot.get("updated_at"),
            )

        logger.info("Normalized repository snapshot", extra={"full_name": data.full_name})
        return data
