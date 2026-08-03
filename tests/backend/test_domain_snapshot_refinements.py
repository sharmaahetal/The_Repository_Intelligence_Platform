import json
from datetime import UTC, datetime, timedelta

import pytest

from backend.app.models.metadata import SnapshotMetadata, compute_snapshot_id
from backend.app.models.snapshot import RepositorySnapshot


def test_deterministic_snapshot_id_computation():
    t1 = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    id1 = compute_snapshot_id(repository_id=12345, snapshot_time=t1, schema_version=1)
    id2 = compute_snapshot_id(repository_id=12345, snapshot_time=t1, schema_version=1)

    assert id1.startswith("snp_")
    assert id1 == id2

    # Different time yields different snapshot_id
    t2 = datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC)
    id3 = compute_snapshot_id(repository_id=12345, snapshot_time=t2, schema_version=1)
    assert id1 != id3


def test_snapshot_metadata_separation():
    t_snap = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    snap = RepositorySnapshot(
        repository_id=99,
        owner="facebook",
        name="react",
        stars=220000,
        forks=45000,
        snapshot_time=t_snap,
        request_id="req-999",
    )

    # Verify metadata sub-model
    assert isinstance(snap.metadata, SnapshotMetadata)
    assert snap.metadata.request_id == "req-999"
    assert snap.metadata.snapshot_time == t_snap
    assert snap.metadata.schema_version == 1
    assert snap.metadata.snapshot_id.startswith("snp_")

    # Verify backwards-compatibility top-level properties
    assert snap.snapshot_id == snap.metadata.snapshot_id
    assert snap.snapshot_time == t_snap
    assert snap.request_id == "req-999"
    assert snap.stars_count == 220000
    assert snap.forks_count == 45000


def test_value_object_equality_and_hashing():
    t_snap = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    snap_a = RepositorySnapshot(
        repository_id=101,
        owner="pallets",
        name="flask",
        stars=65000,
        snapshot_time=t_snap,
    )
    snap_b = RepositorySnapshot(
        repository_id=101,
        owner="pallets",
        name="flask",
        stars=65000,
        snapshot_time=t_snap,
    )

    # Value Object equality
    assert snap_a == snap_b
    assert hash(snap_a) == hash(snap_b)

    # Set deduplication
    snapshot_set = {snap_a, snap_b}
    assert len(snapshot_set) == 1


def test_versioned_serialization():
    t_snap = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    snap = RepositorySnapshot(
        repository_id=55,
        owner="tiangolo",
        name="fastapi",
        stars=70000,
        snapshot_time=t_snap,
    )

    v1_json = snap.to_v1_json()
    assert isinstance(v1_json, str)
    parsed = json.loads(v1_json)

    assert parsed["repository_id"] == 55
    assert parsed["owner"] == "tiangolo"
    assert parsed["name"] == "fastapi"
    assert parsed["metadata"]["snapshot_id"].startswith("snp_")
    assert parsed["schema_version"] == 1


def test_domain_invariant_validation():
    t_snap = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    future_updated_at = t_snap + timedelta(days=5)

    # Violation: updated_at > snapshot_time
    with pytest.raises(ValueError, match="updated_at cannot be after snapshot_time"):
        RepositorySnapshot(
            repository_id=10,
            owner="django",
            name="django",
            snapshot_time=t_snap,
            updated_at=future_updated_at,
        )
