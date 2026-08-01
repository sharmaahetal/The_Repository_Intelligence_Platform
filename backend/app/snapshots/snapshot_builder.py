from datetime import UTC, datetime
from typing import Any

from backend.app.logging import logger
from backend.app.models.domain import RawRepositoryPayload
from backend.app.models.snapshot import RepositorySnapshot


class SnapshotBuilder:
    """Engine for building deterministic point-in-time repository snapshot state S(t_k)."""

    def build_snapshot_from_raw(
        self,
        raw_payload: RawRepositoryPayload | dict[str, Any],
        snapshot_time: datetime,
        request_id: str | None = None,
    ) -> RepositorySnapshot:
        """Constructs deterministic RepositorySnapshot model S(t_k) from validated payload.

        `snapshot_time` must be an explicit, timezone-aware UTC datetime.
        """
        if snapshot_time is None:
            raise ValueError("snapshot_time is required for deterministic snapshot building.")

        if snapshot_time.tzinfo is None or snapshot_time.tzinfo.utcoffset(snapshot_time) is None:
            raise ValueError("snapshot_time must be a timezone-aware UTC datetime.")

        # Ensure timestamp is normalized to UTC timezone
        snapshot_time_utc = snapshot_time.astimezone(UTC)

        if isinstance(raw_payload, RawRepositoryPayload):
            repo_name = raw_payload.name
            owner = raw_payload.owner_login
            full_name = raw_payload.full_name or f"{owner}/{repo_name}"
            stars_count = raw_payload.stargazers_count
            forks_count = raw_payload.forks_count
            open_issues_count = raw_payload.open_issues_count
            subscribers_count = raw_payload.subscribers_count
            size_kb = raw_payload.size
            primary_language = raw_payload.language or "Unknown"
            default_branch = raw_payload.default_branch
            has_wiki = raw_payload.has_wiki
            has_pages = raw_payload.has_pages
            pushed_at = raw_payload.pushed_at
            created_at = raw_payload.created_at
            updated_at = raw_payload.updated_at
        else:
            repo_name = raw_payload.get("name", "")
            owner_val = raw_payload.get("owner", {})
            owner = owner_val.get("login", "") if isinstance(owner_val, dict) else str(owner_val)
            full_name = raw_payload.get("full_name", f"{owner}/{repo_name}")
            stars_count = raw_payload.get("stargazers_count", 0)
            forks_count = raw_payload.get("forks_count", 0)
            open_issues_count = raw_payload.get("open_issues_count", 0)
            subscribers_count = raw_payload.get("subscribers_count", 0)
            size_kb = raw_payload.get("size", 0)
            primary_language = raw_payload.get("language") or "Unknown"
            default_branch = raw_payload.get("default_branch", "main")
            has_wiki = raw_payload.get("has_wiki", False)
            has_pages = raw_payload.get("has_pages", False)
            pushed_at = raw_payload.get("pushed_at")
            created_at = raw_payload.get("created_at")
            updated_at = raw_payload.get("updated_at")

        snapshot = RepositorySnapshot(
            schema_version=1,
            snapshot_timestamp=snapshot_time_utc,
            owner=owner,
            name=repo_name,
            full_name=full_name,
            stars_count=stars_count,
            forks_count=forks_count,
            open_issues_count=open_issues_count,
            subscribers_count=subscribers_count,
            size_kb=size_kb,
            primary_language=primary_language,
            default_branch=default_branch,
            has_wiki=has_wiki,
            has_pages=has_pages,
            pushed_at=pushed_at,
            created_at=created_at,
            updated_at=updated_at,
        )

        logger.info(
            "Built deterministic repository snapshot S(t_k)",
            extra={
                "owner": owner,
                "repo": repo_name,
                "request_id": request_id,
                "snapshot_time": snapshot_time_utc.isoformat(),
            },
        )
        return snapshot
