from backend.app.features.base import BaseFeatureBuilder, feature_builder
from backend.app.features.registry import default_registry
from backend.app.models.feature import Feature, FeatureContext
from backend.app.models.snapshot import RepositorySnapshot


@feature_builder(
    name="repository_builder", version=1, description="Computes repository structural features"
)
class RepositoryBuilder(BaseFeatureBuilder):
    """Pure builder for repository structural features."""

    name = "repository_builder"
    version = 1
    description = "Computes repository structural features"

    async def compute(self, snapshot: RepositorySnapshot, context: FeatureContext) -> list[Feature]:
        size_mb = round(float(snapshot.size_kb) / 1024.0, 4)
        is_large = size_mb >= 500.0

        return [
            Feature(
                name="repository_size_mb",
                value=size_mb,
                dtype="float32",
                version=1,
                description="Repository size in MB",
            ),
            Feature(
                name="is_large_repository",
                value=is_large,
                dtype="bool",
                version=1,
                description="Flag indicating repository size >= 500 MB",
            ),
        ]


repository_builder_instance = default_registry.register(RepositoryBuilder())
