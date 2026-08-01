from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """Immutable model hyper-parameter configuration."""

    model_config = ConfigDict(frozen=True)

    model_name: str = Field(default="repository_growth")
    model_type: str = Field(default="xgboost")
    learning_rate: float = Field(default=0.1)
    max_depth: int = Field(default=6)
    n_estimators: int = Field(default=100)
    subsample: float = Field(default=0.8)
    colsample_bytree: float = Field(default=0.8)
    random_seed: int = Field(default=42)


class TrainingConfig(BaseModel):
    """Immutable training pipeline configuration and validation threshold specifications."""

    model_config = ConfigDict(frozen=True)

    prediction_horizon_days: int = Field(default=180)
    feature_schema_version: int = Field(default=1)
    label_schema_version: int = Field(default=1)
    target_label_name: str = Field(default="is_growth")
    test_ratio: float = Field(default=0.2)
    min_roc_auc_threshold: float = Field(default=0.60)
    min_f1_threshold: float = Field(default=0.50)
