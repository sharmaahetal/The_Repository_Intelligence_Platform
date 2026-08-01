import math
from app.models.feature import Feature


class FeatureValidator:
    """Validator enforcing numerical sanity and type boundaries on computed features."""

    def validate_feature(self, feature: Feature) -> None:
        """Validate feature values against domain boundaries."""
        val = feature.value

        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"Feature '{feature.name}' value is non-finite: {val}")

        if feature.dtype == "int32":
            if isinstance(val, (int, float)) and val < 0:
                raise ValueError(f"Count feature '{feature.name}' cannot be negative: {val}")

        if feature.dtype == "bool":
            if not isinstance(val, bool):
                raise TypeError(f"Boolean feature '{feature.name}' must be bool type, got {type(val)}")
