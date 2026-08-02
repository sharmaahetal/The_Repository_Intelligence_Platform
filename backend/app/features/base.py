from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from backend.app.models.feature import Feature, FeatureContext
from backend.app.models.snapshot import RepositorySnapshot


class BaseFeatureBuilder(ABC):
    """Abstract base class for pure, deterministic feature builders."""

    name: str = "base_builder"
    version: int = 1
    description: str = ""

    @abstractmethod
    async def compute(self, snapshot: RepositorySnapshot, context: FeatureContext) -> list[Feature]:
        """Compute pure features from snapshot and context without side effects."""
        ...


def feature_builder(
    name: str,
    version: int = 1,
    description: str = "",
) -> Callable[[type[BaseFeatureBuilder] | Callable[..., Any]], Any]:
    """Decorator for marking feature builder classes or functions with metadata."""

    def decorator(cls_or_func: Any) -> Any:
        cls_or_func._builder_name = name
        cls_or_func._builder_version = version
        cls_or_func._builder_description = description
        return cls_or_func

    return decorator
