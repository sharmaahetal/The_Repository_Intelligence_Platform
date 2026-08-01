from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.app.models.metadata import SnapshotMetadata
from backend.app.models.raw_payload import RawRepositoryPayload
from backend.app.models.snapshot import RepositorySnapshot


def test_raw_repository_payload_preservation():
    raw_dict = {
        "id": 12345,
        "name": "test-repo",
        "owner": {"login": "test-owner"},
        "stargazers_count": 100,
        "forks_count": 25,
        "open_issues_count": 5,
        "language": "Python",
    }
    headers = {
        "ETag": 'W/"abcdef12345"',
        "X-Request-ID": "req-9999",
        "X-GitHub-Api-Version": "2022-11-28",
        "X-RateLimit-Remaining": "4950",
    }

    payload = RawRepositoryPayload.from_dict(raw_dict, headers=headers)

    assert payload.raw_json == raw_dict
    assert payload.etag == 'W/"abcdef12345"'
    assert payload.request_id == "req-9999"
    assert payload.api_version == "2022-11-28"
    assert payload.rate_limit_remaining == 4950
    assert payload.fetched_at.tzinfo == UTC
    assert payload.name == "test-repo"
    assert payload.owner_login == "test-owner"
    assert payload.stargazers_count == 100


def test_repository_snapshot_immutability_and_utc():
    now_utc = datetime.now(UTC)
    snapshot = RepositorySnapshot(
        repository_id=12345,
        owner="test-owner",
        name="test-repo",
        stars=150,
        forks=30,
        watchers=10,
        issues=4,
        language="TypeScript",
        license="MIT",
        created_at=datetime(2023, 1, 1),  # Naive datetime, should convert to UTC
        updated_at=datetime(2026, 1, 1),
        snapshot_time=now_utc,
    )

    assert snapshot.schema_version == 1
    assert snapshot.repository_id == 12345
    assert snapshot.stars == 150
    assert snapshot.forks == 30
    assert snapshot.created_at.tzinfo == UTC
    assert snapshot.updated_at.tzinfo == UTC
    assert snapshot.snapshot_time == now_utc

    # Verify immutability (frozen=True)
    with pytest.raises(ValidationError):
        snapshot.stars = 200  # Type: ignore


def test_repository_snapshot_aliases_and_validations():
    now = datetime.now(UTC)
    snapshot = RepositorySnapshot(
        repository_id=99,
        owner="org",
        name="project",
        stars_count=50,
        forks_count=12,
        open_issues_count=3,
        subscribers_count=8,
        primary_language="Python",
        created_at=now,
        updated_at=now,
        snapshot_timestamp=now,
    )

    assert snapshot.stars == 50
    assert snapshot.stars_count == 50
    assert snapshot.forks == 12
    assert snapshot.forks_count == 12
    assert snapshot.issues == 3
    assert snapshot.open_issues_count == 3
    assert snapshot.watchers == 8
    assert snapshot.subscribers_count == 8
    assert snapshot.language == "Python"
    assert snapshot.primary_language == "Python"
    assert snapshot.snapshot_time == now
    assert snapshot.snapshot_timestamp == now


def test_snapshot_metadata():
    metadata = SnapshotMetadata(
        request_id="req-123",
        etag='W/"123456"',
        api_version="2022-11-28",
    )

    assert metadata.request_id == "req-123"
    assert metadata.etag == 'W/"123456"'
    assert metadata.collector_version == "1.0.0"
    assert metadata.collected_at.tzinfo == UTC
