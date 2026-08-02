from contextlib import suppress
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RepositorySnapshot(BaseModel):
    """Immutable point-in-time snapshot of a GitHub repository S(t_k).

    Used throughout the ML feature store and training pipeline to guarantee deterministic
    feature computation, temporal anti-leakage guards, and reproducible datasets.
    """

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    schema_version: int = Field(default=1, frozen=True)
    repository_id: int = Field(default=0, description="Unique GitHub repository integer ID")
    owner: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    stars: int = Field(default=0, ge=0)
    forks: int = Field(default=0, ge=0)
    watchers: int = Field(default=0, ge=0)
    issues: int = Field(default=0, ge=0)
    language: str = Field(default="Unknown")
    license: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    snapshot_time: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Auxiliary metadata & backwards compatibility fields
    full_name: str = Field(default="")
    pushed_at: datetime | None = None
    size_kb: int = Field(default=0, ge=0)
    default_branch: str = Field(default="main")
    has_wiki: bool = Field(default=False)
    has_pages: bool = Field(default=False)

    @field_validator("created_at", "updated_at", "snapshot_time", "pushed_at")
    @classmethod
    def validate_utc(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)

    @model_validator(mode="before")
    @classmethod
    def handle_aliases_and_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize string timestamps if passed as string ISO format
            for dt_field in (
                "created_at",
                "updated_at",
                "snapshot_time",
                "snapshot_timestamp",
                "pushed_at",
            ):
                val = data.get(dt_field)
                if isinstance(val, str):
                    with suppress(ValueError):
                        data[dt_field] = datetime.fromisoformat(val.replace("Z", "+00:00"))

            # Handle aliases for backwards compatibility
            if "snapshot_time" not in data and "snapshot_timestamp" in data:
                data["snapshot_time"] = data["snapshot_timestamp"]
            if "stars" not in data and "stars_count" in data:
                data["stars"] = data["stars_count"]
            if "forks" not in data and "forks_count" in data:
                data["forks"] = data["forks_count"]
            if "watchers" not in data and "subscribers_count" in data:
                data["watchers"] = data["subscribers_count"]
            if "issues" not in data and "open_issues_count" in data:
                data["issues"] = data["open_issues_count"]
            if "language" not in data and "primary_language" in data:
                data["language"] = data["primary_language"]
            if not data.get("full_name") and data.get("owner") and data.get("name"):
                data["full_name"] = f"{data['owner']}/{data['name']}"
        return data

    @property
    def snapshot_timestamp(self) -> datetime:
        return self.snapshot_time

    @property
    def stars_count(self) -> int:
        return self.stars

    @property
    def forks_count(self) -> int:
        return self.forks

    @property
    def open_issues_count(self) -> int:
        return self.issues

    @property
    def subscribers_count(self) -> int:
        return self.watchers

    @property
    def primary_language(self) -> str:
        return self.language
