from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


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
