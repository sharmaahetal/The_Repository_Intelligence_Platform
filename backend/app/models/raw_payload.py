from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RawRepositoryPayload(BaseModel):
    """Pydantic model validating raw GitHub API payload and preserving response metadata."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    raw_json: dict[str, Any]
    headers: dict[str, str] = Field(default_factory=dict)
    etag: str | None = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    request_id: str | None = None
    api_version: str | None = None
    rate_limit_remaining: int | None = None

    @model_validator(mode="before")
    @classmethod
    def handle_input_dict(cls, data: Any) -> Any:
        if isinstance(data, dict) and "raw_json" not in data:
            return {"raw_json": data}
        return data

    @field_validator("fetched_at")
    @classmethod
    def validate_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)

    @property
    def name(self) -> str:
        return self.raw_json.get("name", "")

    @property
    def owner(self) -> dict[str, Any] | str:
        return self.raw_json.get("owner", {})

    @property
    def owner_login(self) -> str:
        owner_val = self.raw_json.get("owner", {})
        if isinstance(owner_val, dict):
            return owner_val.get("login", "")
        return str(owner_val)

    @property
    def full_name(self) -> str:
        return self.raw_json.get("full_name") or f"{self.owner_login}/{self.name}"

    @property
    def stargazers_count(self) -> int:
        return self.raw_json.get("stargazers_count", 0)

    @property
    def forks_count(self) -> int:
        return self.raw_json.get("forks_count", 0)

    @property
    def open_issues_count(self) -> int:
        return self.raw_json.get("open_issues_count", 0)

    @property
    def subscribers_count(self) -> int:
        return self.raw_json.get("subscribers_count", 0)

    @property
    def size(self) -> int:
        return self.raw_json.get("size", 0)

    @property
    def language(self) -> str | None:
        return self.raw_json.get("language") or "Unknown"

    @property
    def default_branch(self) -> str:
        return self.raw_json.get("default_branch", "main")

    @property
    def has_wiki(self) -> bool:
        return self.raw_json.get("has_wiki", False)

    @property
    def has_pages(self) -> bool:
        return self.raw_json.get("has_pages", False)

    @property
    def pushed_at(self) -> str | None:
        return self.raw_json.get("pushed_at")

    @property
    def created_at(self) -> str | None:
        return self.raw_json.get("created_at")

    @property
    def updated_at(self) -> str | None:
        return self.raw_json.get("updated_at")

    @classmethod
    def from_dict(cls, data: dict[str, Any], headers: dict[str, str] | None = None) -> "RawRepositoryPayload":
        """Helper to create RawRepositoryPayload directly from a raw GitHub JSON payload dict."""
        hdrs = headers or {}
        remaining_str = hdrs.get("X-RateLimit-Remaining") or hdrs.get("x-ratelimit-remaining") or ""
        remaining = int(remaining_str) if remaining_str.isdigit() else None
        return cls(
            raw_json=data,
            headers=hdrs,
            etag=hdrs.get("ETag") or hdrs.get("etag"),
            request_id=hdrs.get("X-Request-ID") or hdrs.get("x-request-id"),
            api_version=hdrs.get("X-GitHub-Api-Version") or hdrs.get("x-github-api-version"),
            rate_limit_remaining=remaining,
        )


class RawPayload(Base):
    """ORM model storing unmodified GitHub JSON responses and collection metadata."""

    __tablename__ = "raw_payload_store"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    repo_owner: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    collector_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g., 'repository', 'commits', 'issues'
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    etag: Mapped[str | None] = mapped_column(String(100), nullable=True)
    api_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rate_limit_remaining: Mapped[int | None] = mapped_column(Integer, nullable=True)
    headers: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("idx_raw_repo_collector", "repo_owner", "repo_name", "collector_type"),
    )
