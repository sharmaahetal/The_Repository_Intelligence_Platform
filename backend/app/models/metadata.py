from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SnapshotMetadata(BaseModel):
    """Metadata detailing GitHub API collection request context and provenance."""

    model_config = ConfigDict(frozen=True)

    request_id: str | None = None
    etag: str | None = None
    api_version: str | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    collector_version: str = Field(default="1.0.0")

    @field_validator("collected_at")
    @classmethod
    def validate_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)
