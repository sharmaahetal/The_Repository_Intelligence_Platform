from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend.app.collectors.github_client import GitHubResponse
from backend.app.collectors.repository import RepositoryCollector
from backend.app.models.snapshot import RepositorySnapshot
from backend.app.services.snapshot_service import RepositorySnapshotService


@pytest.mark.asyncio
async def test_repository_snapshot_service_orchestration():
    mock_collector = RepositoryCollector()
    mock_collector.fetch_repository = AsyncMock(  # type: ignore
        return_value=GitHubResponse(
            data={
                "name": "kubernetes",
                "owner": {"login": "kubernetes"},
                "full_name": "kubernetes/kubernetes",
                "stargazers_count": 105000,
                "forks_count": 38000,
                "open_issues_count": 2800,
                "subscribers_count": 3400,
                "size": 520000,
                "language": "Go",
                "default_branch": "master",
            },
            headers={"X-GitHub-Api-Version": "2022-11-28", "ETag": 'W/"12345"'},
            status_code=200,
            etag='W/"12345"',
            rate_limit_remaining=4999,
            api_version="2022-11-28",
        )
    )

    service = RepositorySnapshotService(collector=mock_collector)
    t_snapshot = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)

    snapshot = await service.collect_and_build_snapshot(
        owner="kubernetes",
        repo="kubernetes",
        snapshot_time=t_snapshot,
        request_id="req-test-12345",
    )

    assert isinstance(snapshot, RepositorySnapshot)
    assert snapshot.name == "kubernetes"
    assert snapshot.owner == "kubernetes"
    assert snapshot.stars_count == 105000
    assert snapshot.primary_language == "Go"
    assert snapshot.schema_version == 1
    mock_collector.fetch_repository.assert_called_once_with(
        owner="kubernetes", repo="kubernetes", request_id="req-test-12345", etag=None
    )
