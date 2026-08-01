from datetime import UTC, datetime
import pytest

from app.models.snapshot import RepositorySnapshot
from app.snapshots.snapshot_builder import SnapshotBuilder
from pydantic import ValidationError


def test_snapshot_builder_property_determinism():
    raw_payload = {
        "name": "react",
        "owner": {"login": "facebook"},
        "full_name": "facebook/react",
        "stargazers_count": 220000,
        "forks_count": 45000,
        "open_issues_count": 1200,
        "subscribers_count": 6700,
        "size": 180000,
        "language": "JavaScript",
        "default_branch": "main",
    }

    t_snapshot = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)

    builder = SnapshotBuilder()
    snapshot_1 = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_snapshot)
    snapshot_2 = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_snapshot)

    # Identical payloads + identical timestamps must produce 100% equal snapshots
    assert snapshot_1 == snapshot_2
    assert snapshot_1.model_dump() == snapshot_2.model_dump()
    assert snapshot_1.schema_version == 1


def test_snapshot_json_serialization_roundtrip():
    raw_payload = {
        "name": "fastapi",
        "owner": {"login": "tiangolo"},
        "full_name": "tiangolo/fastapi",
        "stargazers_count": 70000,
        "forks_count": 6000,
        "open_issues_count": 400,
        "subscribers_count": 1200,
        "size": 25000,
        "language": "Python",
        "default_branch": "main",
    }

    t_snapshot = datetime(2026, 8, 1, 10, 30, 0, tzinfo=UTC)
    builder = SnapshotBuilder()
    snapshot_original = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_snapshot)

    # Roundtrip: snapshot -> json string -> restored snapshot
    json_data = snapshot_original.model_dump_json()
    snapshot_restored = RepositorySnapshot.model_validate_json(json_data)

    assert snapshot_original == snapshot_restored
    assert snapshot_restored.stars_count == 70000
    assert snapshot_restored.owner == "tiangolo"


def test_snapshot_immutability_frozen():
    raw_payload = {
        "name": "pytorch",
        "owner": {"login": "pytorch"},
        "full_name": "pytorch/pytorch",
        "stargazers_count": 80000,
    }

    t_snapshot = datetime(2026, 8, 1, 0, 0, 0, tzinfo=UTC)
    builder = SnapshotBuilder()
    snapshot = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_snapshot)

    # Attempting to mutate any field on frozen model must raise ValidationError / FrozenInstanceError
    with pytest.raises(ValidationError):
        snapshot.stars_count = 999999  # type: ignore


def test_snapshot_builder_requires_utc_timezone():
    raw_payload = {"name": "repo", "owner": {"login": "owner"}}
    builder = SnapshotBuilder()

    # Naive datetime (no tzinfo) must be rejected
    naive_dt = datetime(2026, 8, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="timezone-aware UTC datetime"):
        builder.build_snapshot_from_raw(raw_payload, snapshot_time=naive_dt)
