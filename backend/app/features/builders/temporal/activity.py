from backend.app.features.base import BaseFeatureBuilder, feature_builder
from backend.app.features.groups import FeatureGroup
from backend.app.features.manifest import FeatureDefinition
from backend.app.features.registry import default_registry
from backend.app.models.feature import Feature, FeatureContext
from backend.app.models.snapshot import RepositorySnapshot


@feature_builder(
    name="activity_builder",
    version=1,
    description="Computes activity & density ratios",
    group=FeatureGroup.ACTIVITY,
)
class ActivityBuilder(BaseFeatureBuilder):
    """Pure builder for activity and density features."""

    name = "activity_builder"
    version = 1
    description = "Computes activity & density ratios"
    group = FeatureGroup.ACTIVITY

    def get_feature_definitions(self) -> list[FeatureDefinition]:
        return [
            FeatureDefinition(
                name="star_density_index",
                version="1.0",
                group=FeatureGroup.ACTIVITY,
                description="Ratio of stargazers relative to repository size in MB",
                dependencies=[],
            ),
            FeatureDefinition(
                name="fork_to_star_ratio",
                version="1.0",
                group=FeatureGroup.ACTIVITY,
                description="Ratio of forks to stargazers",
                dependencies=[],
            ),
            FeatureDefinition(
                name="open_issue_density",
                version="1.0",
                group=FeatureGroup.ACTIVITY,
                description="Ratio of open issues to stargazers",
                dependencies=[],
            ),
            FeatureDefinition(
                name="subscriber_engagement_ratio",
                version="1.0",
                group=FeatureGroup.ACTIVITY,
                description="Ratio of subscribers to stargazers",
                dependencies=[],
            ),
        ]

    async def compute(self, snapshot: RepositorySnapshot, context: FeatureContext) -> list[Feature]:
        stars = float(snapshot.stars_count)
        size_mb = max(1.0, float(snapshot.size_kb) / 1024.0)
        forks = float(snapshot.forks_count)
        issues = float(snapshot.open_issues_count)
        subscribers = float(snapshot.subscribers_count)

        star_density = round(stars / size_mb, 4) if size_mb > 0 else 0.0
        stars_denom = max(1.0, stars)
        fork_star_ratio = round(forks / stars_denom, 4) if stars > 0 else 0.0
        issue_density = round(issues / stars_denom, 4) if stars > 0 else 0.0
        subscriber_ratio = round(subscribers / stars_denom, 4) if stars > 0 else 0.0

        return [
            Feature(
                name="star_density_index",
                value=star_density,
                dtype="float32",
                version=1,
                group=FeatureGroup.ACTIVITY,
                builder=self.name,
                source_snapshot_id=snapshot.snapshot_id,
                description="Ratio of stargazers relative to repository size in MB",
            ),
            Feature(
                name="fork_to_star_ratio",
                value=fork_star_ratio,
                dtype="float32",
                version=1,
                group=FeatureGroup.ACTIVITY,
                builder=self.name,
                source_snapshot_id=snapshot.snapshot_id,
                description="Ratio of forks to stargazers",
            ),
            Feature(
                name="open_issue_density",
                value=issue_density,
                dtype="float32",
                version=1,
                group=FeatureGroup.ACTIVITY,
                builder=self.name,
                source_snapshot_id=snapshot.snapshot_id,
                description="Ratio of open issues to stargazers",
            ),
            Feature(
                name="subscriber_engagement_ratio",
                value=subscriber_ratio,
                dtype="float32",
                version=1,
                group=FeatureGroup.ACTIVITY,
                builder=self.name,
                source_snapshot_id=snapshot.snapshot_id,
                description="Ratio of subscribers to stargazers",
            ),
        ]


activity_builder_instance = default_registry.register(ActivityBuilder())
