from collections.abc import Callable
from typing import Any

from app.logging import logger
from app.models.snapshot import RepositorySnapshot

FeatureBuilderFunc = Callable[[RepositorySnapshot | dict[str, Any]], float]


class FeatureRegistry:
    """Central registry managing pluggable temporal feature builders."""

    def __init__(self, version: str = "v1.0"):
        self.version = version
        self._builders: dict[str, FeatureBuilderFunc] = {}

    def register(self, feature_name: str) -> Callable[[FeatureBuilderFunc], FeatureBuilderFunc]:
        """Decorator to register a feature builder function."""

        def decorator(func: FeatureBuilderFunc) -> FeatureBuilderFunc:
            self._builders[feature_name] = func
            logger.info(
                "Registered feature builder",
                extra={"feature_name": feature_name, "version": self.version},
            )
            return func

        return decorator

    def compute_all(self, snapshot: RepositorySnapshot | dict[str, Any]) -> dict[str, float]:
        """Runs all registered feature builders against a snapshot S(t_k)."""
        feature_vector: dict[str, float] = {}
        for feature_name, builder_func in self._builders.items():
            try:
                feature_vector[feature_name] = float(builder_func(snapshot))
            except Exception as exc:
                logger.warning(
                    "Error computing feature",
                    extra={"feature_name": feature_name, "error": str(exc)},
                )
                feature_vector[feature_name] = 0.0

        return feature_vector

    def get_registered_features(self) -> list[str]:
        return list(self._builders.keys())
