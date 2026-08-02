import math
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.features.groups import FeatureGroup


class Feature(BaseModel):
    """Pydantic immutable model representing a single versioned feature with metadata and provenance."""

    model_config = ConfigDict(frozen=True)

    name: str
    value: float | int | bool | str | None
    dtype: str = Field(default="float32")  # 'float32', 'int32', 'bool', 'string'
    version: int | str = Field(default=1)
    group: FeatureGroup = Field(default=FeatureGroup.ACTIVITY)
    builder: str = Field(default="unknown_builder")
    source_snapshot_id: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def feature_key(self) -> str:
        """Returns versioned feature identifier, e.g., 'fork_to_star_ratio:v1'."""
        return f"{self.name}:v{self.version}"

    @field_validator("value")
    @classmethod
    def validate_non_nan_or_inf(cls, v: float | int | bool | str | None) -> float | int | bool | str | None:
        """Sanity check to prevent NaN or Infinity values."""
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            raise ValueError(f"Feature value cannot be NaN or Infinity, got {v}")
        return v


class FeatureContext:
    """Computation context holding previously evaluated features for dependency sharing."""

    def __init__(self) -> None:
        self._features: dict[str, Feature] = {}

    def add_feature(self, feature: Feature) -> None:
        """Store feature in context by name and feature_key."""
        self._features[feature.name] = feature
        self._features[feature.feature_key] = feature

    def get_value(self, name: str, default: Any = None) -> Any:
        """Retrieve value of a previously computed feature by name or feature_key."""
        if name in self._features:
            return self._features[name].value
        return default

    def has_feature(self, name: str) -> bool:
        """Check if feature has been evaluated in context."""
        return name in self._features


class RepositoryFeatures(BaseModel):
    """Immutable container holding all computed features for a snapshot S(t_k)."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=1, frozen=True)
    snapshot_timestamp: datetime
    features: dict[str, Feature] = Field(default_factory=dict)

    def as_vector(self) -> dict[str, float]:
        """Extract flat dictionary mapping feature names to numerical float values for ML models."""
        vector: dict[str, float] = {}
        for _feat_key, feat in self.features.items():
            if isinstance(feat.value, bool):
                vector[feat.name] = 1.0 if feat.value else 0.0
            elif isinstance(feat.value, int | float):
                vector[feat.name] = float(feat.value)
        return vector

    def get(self, key: str, default: float = 0.0) -> float:
        """Convenience accessor for feature values by name or feature_key."""
        if key in self.features:
            val = self.features[key].value
            if isinstance(val, bool):
                return 1.0 if val else 0.0
            if isinstance(val, int | float):
                return float(val)

        # Search by plain feature name
        for feat in self.features.values():
            if feat.name == key:
                val = feat.value
                if isinstance(val, bool):
                    return 1.0 if val else 0.0
                if isinstance(val, int | float):
                    return float(val)
        return default
