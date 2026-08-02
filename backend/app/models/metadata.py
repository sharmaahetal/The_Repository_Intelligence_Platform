import hashlib
import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def compute_snapshot_id(repository_id: int, snapshot_time: datetime, schema_version: int = 1) -> str:
    """Computes a deterministic snapshot_id from repository_id, snapshot_time ISO string, and schema_version."""
    ts_utc = snapshot_time if snapshot_time.tzinfo else snapshot_time.replace(tzinfo=UTC)
    raw_key = f"{repository_id}:{ts_utc.astimezone(UTC).isoformat()}:{schema_version}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
    return f"snp_{digest}"


class SnapshotMetadata(BaseModel):
    """Metadata detailing GitHub API collection request context, provenance, and deterministic identity."""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str = Field(
        default_factory=lambda: f"snp_{uuid.uuid4().hex[:16]}",
        description="Globally unique deterministic snapshot identity",
    )
    snapshot_time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Explicit, timezone-aware UTC snapshot timestamp S(t_k)",
    )
    schema_version: int = Field(default=1, frozen=True)
    collector_version: str = Field(default="1.0.0")
    request_id: str | None = None
    etag: str | None = None
    api_version: str | None = None

    @field_validator("snapshot_time")
    @classmethod
    def validate_utc(cls, v: datetime) -> datetime:
        if v is None:
            return datetime.now(UTC)
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)

    @property
    def collected_at(self) -> datetime:
        """Backwards compatibility accessor for collected_at timestamp."""
        return self.snapshot_time
