from backend.app.features.base import BaseFeatureBuilder
from backend.app.logging import logger


class FeatureRegistry:
    """Passive registry managing feature builder registrations."""

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


default_registry = FeatureRegistry(version="v1.0")
