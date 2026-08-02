from backend.app.features.registry import FeatureRegistry, default_registry
from backend.app.features.validator import FeatureValidator
from backend.app.logging import logger
from backend.app.models.feature import FeatureContext, RepositoryFeatures
from backend.app.models.snapshot import RepositorySnapshot


class FeaturePipeline:
    """Active orchestrator computing features from snapshots via registered builders."""

    def __init__(
        self,
        registry: FeatureRegistry | None = None,
        validator: FeatureValidator | None = None,
    ):
        self.registry = registry or default_registry
        self.validator = validator or FeatureValidator()

    async def compute_features_async(self, snapshot: RepositorySnapshot) -> RepositoryFeatures:
        """Asynchronously compute all feature vectors for a repository snapshot."""
        if not isinstance(snapshot, RepositorySnapshot):
            raise TypeError(f"FeaturePipeline requires RepositorySnapshot, got {type(snapshot)}")

        context = FeatureContext()
        builders = self.registry.get_builders()
        features_dict = {}

        for builder in builders:
            try:
                computed_list = await builder.compute(snapshot, context)
                for feat in computed_list:
                    # Validate feature bounds & non-NaN sanity
                    self.validator.validate_feature(feat)
                    context.add_feature(feat)
                    features_dict[feat.feature_key] = feat
            except Exception as exc:
                logger.warning(
                    "Error executing feature builder",
                    extra={
                        "builder": getattr(builder, "name", str(builder)),
                        "error": str(exc),
                    },
                )
                raise

        repo_features = RepositoryFeatures(
            schema_version=1,
            snapshot_timestamp=snapshot.snapshot_timestamp,
            features=features_dict,
        )

        logger.info(
            "Successfully computed repository features",
            extra={
                "owner": snapshot.owner,
                "repo": snapshot.name,
                "feature_count": len(features_dict),
            },
        )
        return repo_features

    def compute_features(self, snapshot: RepositorySnapshot) -> RepositoryFeatures:
        """Synchronous wrapper for compute_features_async."""
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If running inside an existing event loop, create task or execute directly
            import nest_asyncio  # type: ignore

            nest_asyncio.apply()
            return loop.run_until_complete(self.compute_features_async(snapshot))
        else:
            return asyncio.run(self.compute_features_async(snapshot))
