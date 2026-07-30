from datetime import UTC, datetime
from typing import Any

from app.logging import logger


class SnapshotBuilder:
    """Engine for building point-in-time repository snapshot state S(t_k)."""

    def build_snapshot_from_raw(
        self,
        raw_payload: dict[str, Any],
        snapshot_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Constructs snapshot state dictionary S(t_k) from raw GitHub payload."""
        snapshot_timestamp = snapshot_time or datetime.now(UTC)

        repo_name = raw_payload.get("name", "")
        owner = raw_payload.get("owner", {}).get("login", "")

        snapshot = {
            "snapshot_timestamp": snapshot_timestamp.isoformat(),
            "owner": owner,
            "name": repo_name,
            "full_name": raw_payload.get("full_name", f"{owner}/{repo_name}"),
            "stars_count": raw_payload.get("stargazers_count", 0),
            "forks_count": raw_payload.get("forks_count", 0),
            "open_issues_count": raw_payload.get("open_issues_count", 0),
            "subscribers_count": raw_payload.get("subscribers_count", 0),
            "size_kb": raw_payload.get("size", 0),
            "primary_language": raw_payload.get("language") or "Unknown",
            "default_branch": raw_payload.get("default_branch", "main"),
            "has_wiki": raw_payload.get("has_wiki", False),
            "has_pages": raw_payload.get("has_pages", False),
            "pushed_at": raw_payload.get("pushed_at"),
            "created_at": raw_payload.get("created_at"),
            "updated_at": raw_payload.get("updated_at"),
        }

        logger.info(
            f"Built snapshot S({snapshot_timestamp.strftime('%Y-%m-%d')}) for {owner}/{repo_name}"
        )
        return snapshot
