from backend.app.features.base import BaseFeatureBuilder
from backend.app.features.dag import FeatureDAG
from backend.app.features.manifest import FeatureManifest
from backend.app.logging import logger


class FeatureRegistry:
    """Passive registry managing feature builder registrations and manifest generation."""

    def __init__(self, version: str = "v1.0"):
        self.version = version
        self._builders: list[BaseFeatureBuilder] = []

    def register(self, builder: BaseFeatureBuilder) -> BaseFeatureBuilder:
        """Register a feature builder instance."""
        self._builders.append(builder)
        logger.info(
            "Registered feature builder",
            extra={
                "builder_name": getattr(builder, "name", str(builder)),
                "version": self.version,
            },
        )
        return builder

    def get_builders(self) -> list[BaseFeatureBuilder]:
        """Return registered builder instances."""
        return list(self._builders)

    def get_manifest(self) -> FeatureManifest:
        """Collects feature definitions from all registered builders and constructs a FeatureManifest."""
        manifest = FeatureManifest(manifest_version=self.version)
        for builder in self._builders:
            definitions = builder.get_feature_definitions()
            for defn in definitions:
                manifest.register_definition(defn)
        return manifest

    def get_dag(self) -> FeatureDAG:
        """Constructs a FeatureDAG engine from all registered feature definitions."""
        manifest = self.get_manifest()
        return FeatureDAG(definitions=list(manifest.definitions.values()))


default_registry = FeatureRegistry(version="v1.0")
