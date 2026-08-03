import json
from contextlib import suppress
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.app.models.metadata import SnapshotMetadata, compute_snapshot_id


class RepositorySnapshot(BaseModel):
    """Immutable point-in-time snapshot of a GitHub repository S(t_k) behaving as a Value Object.

    Used throughout the ML feature store and training pipeline to guarantee deterministic
    feature computation, temporal anti-leakage guards, and reproducible datasets.
    """

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    repository_id: int = Field(default=0, ge=0, description="Unique GitHub repository integer ID")
    owner: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    full_name: str = Field(default="")
    stars: int = Field(default=0, ge=0)
    forks: int = Field(default=0, ge=0)
    watchers: int = Field(default=0, ge=0)
    issues: int = Field(default=0, ge=0)
    language: str = Field(default="Unknown")
    license: str | None = None
    size_kb: int = Field(default=0, ge=0)
    default_branch: str = Field(default="main")
    has_wiki: bool = Field(default=False)
    has_pages: bool = Field(default=False)

    created_at: datetime | None = None
    updated_at: datetime | None = None
    pushed_at: datetime | None = None

    metadata: SnapshotMetadata

    @field_validator("created_at", "updated_at", "pushed_at")
    @classmethod
    def validate_utc(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)

    @model_validator(mode="after")
    def validate_domain_invariants(self) -> "RepositorySnapshot":
        if (
            self.updated_at
            and self.metadata
            and self.metadata.snapshot_time
            and self.updated_at > self.metadata.snapshot_time
        ):
            raise ValueError("Domain invariant violation: updated_at cannot be after snapshot_time")
        return self

    @model_validator(mode="before")
    @classmethod
    def handle_aliases_and_metadata_construction(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Normalize string timestamps
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

            # 2. Extract or build metadata sub-model
            meta = data.get("metadata")
            if not isinstance(meta, SnapshotMetadata | dict):
                t_snap = (
                    data.get("snapshot_time")
                    or data.get("snapshot_timestamp")
                    or datetime.now(UTC)
                )
                if isinstance(t_snap, str):
                    with suppress(ValueError):
                        t_snap = datetime.fromisoformat(t_snap.replace("Z", "+00:00"))

                t_snap_dt = t_snap if isinstance(t_snap, datetime) else datetime.now(UTC)
                repo_id = int(data.get("repository_id") or data.get("id") or 0)
                schema_ver = int(data.get("schema_version") or 1)
                snap_id = data.get("snapshot_id") or compute_snapshot_id(repo_id, t_snap_dt, schema_ver)

                data["metadata"] = {
                    "snapshot_id": snap_id,
                    "snapshot_time": t_snap,
                    "schema_version": schema_ver,
                    "collector_version": str(data.get("collector_version") or "1.0.0"),
                    "request_id": data.get("request_id"),
                    "etag": data.get("etag"),
                    "api_version": data.get("api_version"),
                }

            # 3. Aliases & fallbacks
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

    # Backwards-compatibility properties delegating to metadata
    @property
    def snapshot_id(self) -> str:
        return self.metadata.snapshot_id

    @property
    def snapshot_time(self) -> datetime:
        return self.metadata.snapshot_time

    @property
    def snapshot_timestamp(self) -> datetime:
        return self.metadata.snapshot_time

    @property
    def schema_version(self) -> int:
        return self.metadata.schema_version

    @property
    def request_id(self) -> str | None:
        return self.metadata.request_id

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

    # Explicit Versioned Serialization Methods
    def to_v1_json(self) -> str:
        """Serializes snapshot model to explicit v1 JSON schema format."""
        d = self.to_dict()
        d["schema_version"] = 1
        return json.dumps(d, default=str)

    def to_dict(self) -> dict[str, Any]:
        """Returns snapshot data dictionary including nested metadata dictionary."""
        return self.model_dump(mode="python")

    # Value Object Equality & Hashing Overrides
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RepositorySnapshot):
            return False
        return (
            self.repository_id == other.repository_id
            and self.owner == other.owner
            and self.name == other.name
            and self.stars == other.stars
            and self.forks == other.forks
            and self.watchers == other.watchers
            and self.issues == other.issues
            and self.language == other.language
            and self.metadata == other.metadata
        )

    def __hash__(self) -> int:
        return hash((self.repository_id, self.metadata.snapshot_id, self.metadata.snapshot_time))
