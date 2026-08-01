from datetime import UTC, datetime
import pytest

from app.models.snapshot import RepositorySnapshot
from app.normalizers.normalizer import SnapshotNormalizer
from app.snapshots.snapshot_builder import SnapshotBuilder


def test_historical_snapshot_pipeline():
    # 1. Mock raw GitHub API payload
    raw_payload = {
        "name": "vscode",
        "owner": {"login": "microsoft"},
        "full_name": "microsoft/vscode",
        "stargazers_count": 155000,
        "forks_count": 28000,
        "open_issues_count": 4500,
        "subscribers_count": 3100,
        "size": 450000,
        "language": "TypeScript",
        "default_branch": "main",
        "has_wiki": True,
        "has_pages": False,
        "pushed_at": "2026-07-30T12:00:00Z",
        "created_at": "2015-09-03T20:23:38Z",
    }

    t_snapshot = datetime(2026, 7, 30, 0, 0, 0, tzinfo=UTC)

    # 2. Build snapshot S(t_0)
    builder = SnapshotBuilder()
    snapshot = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_snapshot)

    assert isinstance(snapshot, RepositorySnapshot)
    assert snapshot.name == "vscode"
    assert snapshot.owner == "microsoft"
    assert snapshot.stars_count == 155000
    assert snapshot.primary_language == "TypeScript"

    # Test dictionary-like subscript access for backwards compatibility
    assert snapshot["name"] == "vscode"
    assert snapshot["stars_count"] == 155000

    # 3. Normalize snapshot
    normalizer = SnapshotNormalizer()
    normalized = normalizer.normalize(snapshot)

    assert normalized.full_name == "microsoft/vscode"
    assert normalized.stars_count == 155000
    assert normalized.primary_language == "TypeScript"
    assert normalized.has_wiki is True


def test_snapshot_builder_requires_explicit_timestamp():
    raw_payload = {"name": "repo", "owner": {"login": "owner"}}
    builder = SnapshotBuilder()
    with pytest.raises(TypeError):
        # Missing required parameter snapshot_time
        builder.build_snapshot_from_raw(raw_payload)  # type: ignore
