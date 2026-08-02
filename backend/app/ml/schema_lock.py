from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FeatureSchemaMismatchError(ValueError):
    """Raised when incoming inference feature vector does not match the locked feature schema."""

    pass


class FeatureSchemaLock(BaseModel):
    """Schema lock ensuring trained models strictly validate incoming feature vector schemas."""

    model_config = ConfigDict(frozen=True)

    model_name: str = Field(..., description="Model identifier name")
    schema_version: int = Field(default=1, description="Feature schema version number")
    expected_features: list[str] = Field(..., description="List of required feature names")
    feature_dtypes: dict[str, str] = Field(default_factory=dict, description="Expected feature dtypes")

    def validate_schema(self, input_features: list[str] | dict[str, Any]) -> None:
        """Validates that all expected features exist in input_features.

        Raises FeatureSchemaMismatchError if required features are missing.
        """
        if isinstance(input_features, dict):
            present_set = set(input_features.keys())
        elif isinstance(input_features, list):
            present_set = set(input_features)
        else:
            raise TypeError(f"input_features must be list or dict, got {type(input_features)}")

        missing = [f for f in self.expected_features if f not in present_set]
        if missing:
            raise FeatureSchemaMismatchError(
                f"Feature Schema Mismatch for model '{self.model_name}' (v{self.schema_version}): "
                f"Missing required features: {missing}"
            )
