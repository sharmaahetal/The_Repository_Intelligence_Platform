"""Repository snapshot ORM domain model for Repository Intelligence Platform.

Captures point-in-time time-series snapshots of repository metrics.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.database.models.prediction import Prediction
    from backend.app.database.models.repository import Repository


class RepositorySnapshot(Base, TimestampMixin):
    """Repository snapshot entity storing metric counts at a specific point in time."""

    __tablename__ = "repository_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    snapshot_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp representing when the repository state snapshot occurred",
    )
    stars: Mapped[int] = mapped_column(default=0, nullable=False)
    forks: Mapped[int] = mapped_column(default=0, nullable=False)
    watchers: Mapped[int] = mapped_column(default=0, nullable=False)
    open_issues: Mapped[int] = mapped_column(default=0, nullable=False)
    subscribers: Mapped[int] = mapped_column(default=0, nullable=False)
    network_count: Mapped[int] = mapped_column(default=0, nullable=False)
    size_kb: Mapped[int] = mapped_column(default=0, nullable=False)
    license: Mapped[str | None] = mapped_column(String(50), nullable=True)
    topics_json: Mapped[dict[str, Any] | list[str] | None] = mapped_column(JSON, nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(
        back_populates="snapshots",
    )
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_repository_snapshots_repo_snapshot_time", "repository_id", "snapshot_time"),
        CheckConstraint("stars >= 0", name="stars_non_negative"),
        CheckConstraint("forks >= 0", name="forks_non_negative"),
        CheckConstraint("open_issues >= 0", name="open_issues_non_negative"),
    )
