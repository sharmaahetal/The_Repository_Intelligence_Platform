from backend.app.features.base import BaseFeatureBuilder, feature_builder
from backend.app.features.registry import default_registry
from backend.app.models.feature import Feature, FeatureContext
from backend.app.models.snapshot import RepositorySnapshot


@feature_builder(name="community_builder", version=1, description="Computes community features")
class CommunityBuilder(BaseFeatureBuilder):
    """Pure builder for community features."""

    name = "community_builder"
    version = 1
    description = "Computes community features"

    async def compute(self, snapshot: RepositorySnapshot, context: FeatureContext) -> list[Feature]:
        return [
            Feature(
                name="has_wiki_enabled",
                value=bool(snapshot.has_wiki),
                dtype="bool",
                version=1,
                description="Whether repository wiki is enabled",
            ),
            Feature(
                name="has_pages_enabled",
                value=bool(snapshot.has_pages),
                dtype="bool",
                version=1,
                description="Whether repository GitHub Pages is enabled",
            ),
        ]


community_builder_instance = default_registry.register(CommunityBuilder())
