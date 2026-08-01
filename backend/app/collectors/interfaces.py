from typing import Any, Protocol
from app.models.domain import RawRepositoryPayload
from app.models.snapshot import RepositorySnapshot


class GitHubProvider(Protocol):
    """Protocol interface for fetching raw repository data from a provider (e.g. GitHub, GitLab)."""

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        ...


class SnapshotStorage(Protocol):
    """Protocol interface for snapshot storage backends."""

    async def save_snapshot(self, snapshot: RepositorySnapshot) -> None:
        ...

    async def get_latest_snapshot(self, owner: str, repo: str) -> RepositorySnapshot | None:
        ...
