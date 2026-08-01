from datetime import UTC, datetime

import pytest

import backend.app.features.builders.temporal.activity  # noqa: F401
from backend.app.features.pipeline import FeaturePipeline
from backend.app.snapshots.snapshot_builder import SnapshotBuilder


@pytest.mark.asyncio
async def test_feature_registry_extraction():
    raw_payload = {
        "name": "vscode",
        "owner": {"login": "microsoft"},
        "full_name": "microsoft/vscode",
        "stargazers_count": 100000,
        "forks_count": 25000,
        "open_issues_count": 5000,
        "subscribers_count": 2000,
        "size": 512000,  # 500 MB
        "language": "TypeScript",
        "default_branch": "main",
    }

    t_snapshot = datetime(2026, 7, 30, 0, 0, 0, tzinfo=UTC)
    builder = SnapshotBuilder()
    snapshot = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_snapshot)

    # Compute feature vector via FeaturePipeline
    pipeline = FeaturePipeline()
    repo_features = await pipeline.compute_features_async(snapshot)
    feature_vector = repo_features.as_vector()

    # Assert feature keys exist
    assert "star_density_index" in feature_vector
    assert "fork_to_star_ratio" in feature_vector
    assert "open_issue_density" in feature_vector
    assert "subscriber_engagement_ratio" in feature_vector

    # Assert expected math outputs
    # forks (25,000) / stars (100,000) = 0.25
    assert feature_vector["fork_to_star_ratio"] == 0.25

    # issues (5,000) / stars (100,000) = 0.05
    assert feature_vector["open_issue_density"] == 0.05

    # subscribers (2,000) / stars (100,000) = 0.02
    assert feature_vector["subscriber_engagement_ratio"] == 0.02
