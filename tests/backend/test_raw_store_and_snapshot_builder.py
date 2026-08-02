from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.raw_payload import RawRepositoryPayload
from backend.app.raw_store.raw_payload_repository import RawPayloadRepository
from backend.app.snapshots.snapshot_builder import SnapshotBuilder


@pytest.mark.asyncio
async def test_raw_payload_repository_persistence():
    mock_session = AsyncMock(spec=AsyncSession)

    repo = RawPayloadRepository(session=mock_session)
    raw_payload = RawRepositoryPayload.from_dict(
        {"id": 555, "name": "cpython", "owner": {"login": "python"}},
        headers={"ETag": 'W/"123"', "X-Request-ID": "req-py"},
    )

    saved = await repo.save_raw_payload(
        owner="python",
        repo="cpython",
        collector_type="repository",
        raw_json=raw_payload,
    )

    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called
    assert saved.repo_owner == "python"
    assert saved.repo_name == "cpython"
    assert saved.etag == 'W/"123"'


def test_snapshot_builder_determinism_and_purity():
    builder = SnapshotBuilder()
    snapshot_time = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)

    raw_payload = RawRepositoryPayload.from_dict(
        {
            "id": 98765,
            "name": "scikit-learn",
            "owner": {"login": "scikit-learn"},
            "full_name": "scikit-learn/scikit-learn",
            "stargazers_count": 55000,
            "forks_count": 25000,
            "open_issues_count": 1200,
            "subscribers_count": 2000,
            "language": "Python",
            "license": {"spdx_id": "BSD-3-Clause"},
            "created_at": "2010-01-01T00:00:00Z",
            "updated_at": "2026-08-01T10:00:00Z",
        }
    )

    snapshot_1 = builder.build_snapshot_from_raw(raw_payload, snapshot_time=snapshot_time)
    snapshot_2 = builder.build_snapshot_from_raw(raw_payload, snapshot_time=snapshot_time)

    # Property test: Same input + same timestamp MUST yield exact same snapshot
    assert snapshot_1 == snapshot_2
    assert snapshot_1.repository_id == 98765
    assert snapshot_1.owner == "scikit-learn"
    assert snapshot_1.name == "scikit-learn"
    assert snapshot_1.stars == 55000
    assert snapshot_1.forks == 25000
    assert snapshot_1.watchers == 2000
    assert snapshot_1.issues == 1200
    assert snapshot_1.language == "Python"
    assert snapshot_1.license == "BSD-3-Clause"
    assert snapshot_1.snapshot_time == snapshot_time
    assert snapshot_1.schema_version == 1


def test_snapshot_builder_rejects_naive_timestamp():
    builder = SnapshotBuilder()
    raw_payload = {"name": "repo", "owner": {"login": "owner"}}

    with pytest.raises(ValueError, match="snapshot_time is required"):
        builder.build_snapshot_from_raw(raw_payload, snapshot_time=None)  # type: ignore

    naive_time = datetime(2026, 8, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="must be a timezone-aware UTC datetime"):
        builder.build_snapshot_from_raw(raw_payload, snapshot_time=naive_time)
