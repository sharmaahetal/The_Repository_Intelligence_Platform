from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

# Import builders to register them with default_registry
import backend.app.features.builders.temporal.activity  # noqa: F401
import backend.app.features.builders.temporal.community  # noqa: F401
import backend.app.features.builders.temporal.repository  # noqa: F401
from backend.app.features.pipeline import FeaturePipeline
from backend.app.features.validator import FeatureValidator
from backend.app.models.feature import Feature, RepositoryFeatures
from backend.app.models.snapshot import RepositorySnapshot
from backend.app.snapshots.snapshot_builder import SnapshotBuilder


@pytest.fixture
def sample_snapshot() -> RepositorySnapshot:
    builder = SnapshotBuilder()
    raw = {
        "name": "vscode",
        "owner": {"login": "microsoft"},
        "full_name": "microsoft/vscode",
        "stargazers_count": 150000,
        "forks_count": 25000,
        "open_issues_count": 5000,
        "subscribers_count": 3000,
        "size": 512000,  # 500 MB
        "language": "TypeScript",
        "default_branch": "main",
        "has_wiki": True,
        "has_pages": False,
    }
    t_snapshot = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    return builder.build_snapshot_from_raw(raw, snapshot_time=t_snapshot)


@pytest.mark.asyncio
async def test_feature_pipeline_determinism(sample_snapshot: RepositorySnapshot):
    pipeline = FeaturePipeline()
    features_1 = await pipeline.compute_features_async(sample_snapshot)
    features_2 = await pipeline.compute_features_async(sample_snapshot)

    assert isinstance(features_1, RepositoryFeatures)
    assert features_1 == features_2
    assert features_1.model_dump() == features_2.model_dump()


@pytest.mark.asyncio
async def test_feature_schema_stability_and_types(sample_snapshot: RepositorySnapshot):
    pipeline = FeaturePipeline()
    features = await pipeline.compute_features_async(sample_snapshot)

    assert "star_density_index:v1" in features.features
    assert "fork_to_star_ratio:v1" in features.features
    assert "has_wiki_enabled:v1" in features.features
    assert "repository_size_mb:v1" in features.features

    fork_feat = features.features["fork_to_star_ratio:v1"]
    assert fork_feat.dtype == "float32"
    assert fork_feat.version == 1
    assert fork_feat.value == 0.1667

    wiki_feat = features.features["has_wiki_enabled:v1"]
    assert wiki_feat.dtype == "bool"
    assert wiki_feat.value is True

    vector = features.as_vector()
    assert "fork_to_star_ratio" in vector
    assert vector["fork_to_star_ratio"] == 0.1667


@pytest.mark.asyncio
async def test_repository_features_json_serialization(sample_snapshot: RepositorySnapshot):
    pipeline = FeaturePipeline()
    features_orig = await pipeline.compute_features_async(sample_snapshot)

    json_str = features_orig.model_dump_json()
    features_restored = RepositoryFeatures.model_validate_json(json_str)

    assert features_orig == features_restored
    assert features_restored.get("fork_to_star_ratio") == 0.1667


@pytest.mark.asyncio
async def test_feature_edge_cases_zero_counts():
    builder = SnapshotBuilder()
    raw_zero = {
        "name": "empty_repo",
        "owner": {"login": "dev"},
        "full_name": "dev/empty_repo",
        "stargazers_count": 0,
        "forks_count": 0,
        "open_issues_count": 0,
        "subscribers_count": 0,
        "size": 0,
    }
    t_snapshot = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    snapshot = builder.build_snapshot_from_raw(raw_zero, snapshot_time=t_snapshot)

    pipeline = FeaturePipeline()
    features = await pipeline.compute_features_async(snapshot)

    assert features.get("star_density_index") == 0.0
    assert features.get("fork_to_star_ratio") == 0.0
    assert features.get("open_issue_density") == 0.0


def test_feature_validator_rejects_nan_and_inf():
    validator = FeatureValidator()

    with pytest.raises(ValidationError):
        Feature(name="invalid_nan", value=float("nan"))

    with pytest.raises(ValidationError):
        Feature(name="invalid_inf", value=float("inf"))

    with pytest.raises(ValueError, match="cannot be negative"):
        bad_count_feat = Feature(name="negative_count", value=-10, dtype="int32")
        validator.validate_feature(bad_count_feat)
