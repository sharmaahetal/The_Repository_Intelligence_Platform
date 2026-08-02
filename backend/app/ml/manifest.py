import platform
import subprocess
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TrainingManifest(BaseModel):
    """Reproducible training manifest capturing environment, dataset lineage, hyperparameters, and evaluation metrics."""

    model_config = ConfigDict(frozen=True)

    model_name: str
    model_version: str = Field(default="v1.0.0")
    dataset_version: str = Field(default="v1.0")
    dataset_hash: str = Field(default="")
    feature_schema_version: int = Field(default=1)
    git_commit: str = Field(default_factory=lambda: TrainingManifest._get_git_commit())
    python_version: str = Field(default_factory=lambda: platform.python_version())
    xgboost_version: str = Field(default_factory=lambda: TrainingManifest._get_xgboost_version())
    trained_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    parameters: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    feature_names: list[str] = Field(default_factory=list)

    @staticmethod
    def _get_git_commit() -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return "unknown"

    @staticmethod
    def _get_xgboost_version() -> str:
        try:
            import xgboost  # type: ignore

            return str(getattr(xgboost, "__version__", "unknown"))
        except ImportError:
            return "not_installed"
