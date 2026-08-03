from datetime import UTC, datetime

import pytest

from backend.app.features import (
    FeatureCycleError,
    FeatureDAG,
    FeatureDefinition,
    FeatureGroup,
    FeatureManifest,
    FeaturePipeline,
    FeatureRegistry,
)
from backend.app.features.builders.temporal.activity import ActivityBuilder
from backend.app.models.feature import Feature
from backend.app.models.snapshot import RepositorySnapshot


def test_feature_manifest_documentation_and_dependency_graph():
    manifest = FeatureManifest(manifest_version="1.0.0")

    def1 = FeatureDefinition(
        name="stars_count",
        version="1.0",
        group=FeatureGroup.POPULARITY,
        description="Raw stargazers count",
        dependencies=[],
    )
    def2 = FeatureDefinition(
        name="fork_to_star_ratio",
        version="1.0",
        group=FeatureGroup.ACTIVITY,
        description="Forks divided by stars",
        dependencies=["stars_count"],
    )

    manifest.register_definition(def1)
    manifest.register_definition(def2)

    doc = manifest.generate_documentation()
    assert doc["total_features"] == 2
    assert "stars_count" in doc["features"]
    assert "fork_to_star_ratio" in doc["features"]

    graph = manifest.generate_dependency_graph()
    assert graph["stars_count"] == []
    assert graph["fork_to_star_ratio"] == ["stars_count"]


def test_feature_dag_topological_sort_and_cycle_detection():
    # Linear chain: C depends on B, B depends on A
    def_a = FeatureDefinition(name="feat_A", dependencies=[])
    def_b = FeatureDefinition(name="feat_B", dependencies=["feat_A"])
    def_c = FeatureDefinition(name="feat_C", dependencies=["feat_B"])

    dag = FeatureDAG(definitions=[def_c, def_b, def_a])
    order = dag.topological_sort()

    # feat_A must come before feat_B, and feat_B before feat_C
    assert order.index("feat_A") < order.index("feat_B")
    assert order.index("feat_B") < order.index("feat_C")

    # Circular dependency detection
    cyclic_a = FeatureDefinition(name="feat_X", dependencies=["feat_Y"])
    cyclic_b = FeatureDefinition(name="feat_Y", dependencies=["feat_X"])
    cyclic_dag = FeatureDAG(definitions=[cyclic_a, cyclic_b])

    with pytest.raises(FeatureCycleError):
        cyclic_dag.topological_sort()


def test_rich_feature_provenance():
    t_now = datetime.now(UTC)
    feat = Feature(
        name="test_metric",
        value=42.0,
        group=FeatureGroup.GROWTH,
        builder="growth_builder",
        source_snapshot_id="snp_abc123",
        dependencies=["raw_stars"],
        created_at=t_now,
    )

    assert feat.name == "test_metric"
    assert feat.value == 42.0
    assert feat.group == FeatureGroup.GROWTH
    assert feat.builder == "growth_builder"
    assert feat.source_snapshot_id == "snp_abc123"
    assert feat.dependencies == ["raw_stars"]
    assert feat.created_at == t_now


@pytest.mark.asyncio
async def test_feature_pipeline_dag_execution():
    registry = FeatureRegistry(version="v1.0")
    registry.register(ActivityBuilder())

    pipeline = FeaturePipeline(registry=registry)
    t_snap = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    snapshot = RepositorySnapshot(
        repository_id=500,
        owner="google",
        name="jax",
        stars=28000,
        forks=2500,
        snapshot_time=t_snap,
    )

    repo_features = await pipeline.compute_features_async(snapshot)
    assert len(repo_features.features) > 0

    # Verify provenance metadata attached to output features
    feat = repo_features.features.get("fork_to_star_ratio:v1")
    assert feat is not None
    assert feat.builder == "activity_builder"
    assert feat.source_snapshot_id == snapshot.snapshot_id
    assert feat.group == FeatureGroup.ACTIVITY
