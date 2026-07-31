from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.logging import logger


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
    """Engine for normalizing snapshot dictionaries into typed dataclasses."""

    def normalize(self, snapshot: dict[str, Any]) -> NormalizedRepositoryData:
        """Normalizes raw snapshot dictionary into NormalizedRepositoryData."""
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
            snapshot_timestamp=snapshot.get("snapshot_timestamp", datetime.now(UTC).isoformat()),
            pushed_at=snapshot.get("pushed_at"),
            created_at=snapshot.get("created_at"),
            updated_at=snapshot.get("updated_at"),
        )
        logger.info(f"Normalized snapshot for {data.full_name}")
        return data
