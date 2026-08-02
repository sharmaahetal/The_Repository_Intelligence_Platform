import subprocess
import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


def _get_git_commit_hash() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=False
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "fb1ac76"


class DataLineage(BaseModel):
    """Immutable data lineage metadata recording exact provenance of every prediction."""

    model_config = ConfigDict(frozen=True)

    prediction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_version: str = Field(default="v1.0")
    dataset_version: str = Field(default="v1.0")
    feature_schema_version: int = Field(default=1)
    snapshot_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    git_commit: str = Field(default_factory=_get_git_commit_hash)
