from datetime import UTC, datetime
from typing import Any

from backend.app.logging import logger
from backend.app.models.raw_payload import RawRepositoryPayload
from backend.app.models.snapshot import RepositorySnapshot


class SnapshotBuilder:
    """Engine for building deterministic point-in-time repository snapshot state S(t_k).

    Pure function transformer: RawRepositoryPayload + snapshot_time -> RepositorySnapshot.
    Never uses datetime.now() inside.
    """

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

        if not isinstance(snapshot_time, datetime):
            raise TypeError(f"snapshot_time must be a datetime instance, got {type(snapshot_time)}")

        if snapshot_time.tzinfo is None or snapshot_time.tzinfo.utcoffset(snapshot_time) is None:
            raise ValueError("snapshot_time must be a timezone-aware UTC datetime.")

        # Ensure timestamp is normalized to UTC timezone
        snapshot_time_utc = snapshot_time.astimezone(UTC)

        if isinstance(raw_payload, RawRepositoryPayload):
            repo_dict = raw_payload.raw_json
        elif isinstance(raw_payload, dict):
            repo_dict = raw_payload
        else:
            raise TypeError(
                f"raw_payload must be RawRepositoryPayload or dict, got {type(raw_payload)}"
            )

        repo_id = repo_dict.get("id", 0)
        repo_name = repo_dict.get("name", "")
        owner_val = repo_dict.get("owner", {})
        owner = owner_val.get("login", "") if isinstance(owner_val, dict) else str(owner_val)
        full_name = repo_dict.get("full_name") or f"{owner}/{repo_name}"
        stars = int(repo_dict.get("stargazers_count") or 0)
        forks = int(repo_dict.get("forks_count") or 0)
        watchers_raw = (
            repo_dict.get("subscribers_count")
            if repo_dict.get("subscribers_count") is not None
            else repo_dict.get("watchers_count", 0)
        )
        watchers = int(watchers_raw or 0)
        issues = int(repo_dict.get("open_issues_count") or 0)
        language = str(repo_dict.get("language") or "Unknown")

        license_val = repo_dict.get("license")
        license_spdx = (
            license_val.get("spdx_id")
            if isinstance(license_val, dict)
            else str(license_val)
            if license_val
            else None
        )

        size_kb = int(repo_dict.get("size") or 0)
        default_branch = repo_dict.get("default_branch", "main")
        has_wiki = repo_dict.get("has_wiki", False)
        has_pages = repo_dict.get("has_pages", False)

        pushed_at = repo_dict.get("pushed_at")
        created_at = repo_dict.get("created_at")
        updated_at = repo_dict.get("updated_at")

        snapshot = RepositorySnapshot(
            schema_version=1,
            repository_id=repo_id,
            owner=owner,
            name=repo_name,
            full_name=full_name,
            stars=stars,
            forks=forks,
            watchers=watchers,
            issues=issues,
            language=language,
            license=license_spdx,
            size_kb=size_kb,
            default_branch=default_branch,
            has_wiki=has_wiki,
            has_pages=has_pages,
            pushed_at=pushed_at,
            created_at=created_at,
            updated_at=updated_at,
            snapshot_time=snapshot_time_utc,
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
