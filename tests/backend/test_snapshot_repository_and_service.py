from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend.app.collectors.github_client import GitHubResponse
from backend.app.collectors.repository_collector import RepositoryCollector
from backend.app.models.snapshot import RepositorySnapshot
from backend.app.snapshots.snapshot_builder import SnapshotBuilder
from backend.app.snapshots.snapshot_repository import SnapshotRepository
from backend.app.snapshots.snapshot_service import SnapshotService


@pytest.mark.asyncio
async def test_snapshot_repository_operations():
    repo = SnapshotRepository()
    t1 = datetime(2026, 8, 1, 10, 0, 0, tzinfo=UTC)
    t2 = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)

    s1 = RepositorySnapshot(
        repository_id=1,
        owner="golang",
        name="go",
        stars=110000,
        forks=17000,
        created_at=t1,
        updated_at=t1,
        snapshot_time=t1,
    )

    s2 = RepositorySnapshot(
        repository_id=1,
        owner="golang",
        name="go",
        stars=110500,
        forks=17100,
        created_at=t1,
        updated_at=t2,
        snapshot_time=t2,
    )

    await repo.save_snapshot(s1)
    await repo.save_snapshot(s2)

    latest = await repo.get_latest_snapshot("golang", "go")
    assert latest is not None
    assert latest.stars == 110500
    assert latest.snapshot_time == t2

    specific = await repo.get_snapshot_at_time("golang", "go", t1)
    assert specific is not None
    assert specific.stars == 110000

    notFound = await repo.get_latest_snapshot("golang", "nonexistent")
    assert notFound is None


@pytest.mark.asyncio
async def test_snapshot_service_full_pipeline():
    mock_client = AsyncMock()
    mock_client.is_closed = False
    mock_client.get.return_value = GitHubResponse(
        data={
            "id": 101,
            "name": "kubernetes",
            "owner": {"login": "kubernetes"},
            "stargazers_count": 105000,
            "forks_count": 38000,
            "open_issues_count": 2800,
            "subscribers_count": 3400,
            "language": "Go",
        },
        headers={"ETag": 'W/"k8s-etag"', "X-Request-ID": "req-k8s"},
        status_code=200,
    )

    collector = RepositoryCollector(client=mock_client)
    snapshot_repo = SnapshotRepository()
    builder = SnapshotBuilder()

    service = SnapshotService(
        collector=collector,
        builder=builder,
        snapshot_repository=snapshot_repo,
    )

    t_snap = datetime(2026, 8, 1, 14, 0, 0, tzinfo=UTC)
    snapshot = await service.collect_and_build_snapshot(
        owner="kubernetes",
        repo="kubernetes",
        snapshot_time=t_snap,
        request_id="req-k8s",
    )

    assert isinstance(snapshot, RepositorySnapshot)
    assert snapshot.repository_id == 101
    assert snapshot.owner == "kubernetes"
    assert snapshot.name == "kubernetes"
    assert snapshot.stars == 105000
    assert snapshot.forks == 38000
    assert snapshot.snapshot_time == t_snap

    # Verify persisted in SnapshotRepository
    stored_snapshot = await snapshot_repo.get_latest_snapshot("kubernetes", "kubernetes")
    assert stored_snapshot is not None
    assert stored_snapshot.stars == 105000
