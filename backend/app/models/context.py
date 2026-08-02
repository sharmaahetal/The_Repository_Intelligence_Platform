import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class PredictionContext(BaseModel):
    """Context container propagated across prediction pipeline stages."""

    model_config = ConfigDict(frozen=True)

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    owner: str
    repo: str
    horizon: int = Field(default=180)
    api_version: str = Field(default="v1")
    model_version: str = Field(default="v1.0")
    snapshot_id: str | None = None
    feature_schema_version: int = Field(default=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
