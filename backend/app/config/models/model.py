from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """Machine learning model registry and prediction configuration."""

    model_config = ConfigDict(populate_by_name=True)

    model_registry_path: str = Field(
        default="artifacts/registry",
        validation_alias=AliasChoices("MODEL_REGISTRY_PATH", "MODEL_PATH", "MODEL__MODEL_REGISTRY_PATH"),
    )
    default_model_version: str = Field(
        default="v1.0",
        validation_alias=AliasChoices("DEFAULT_MODEL_VERSION", "MODEL__DEFAULT_MODEL_VERSION"),
    )
