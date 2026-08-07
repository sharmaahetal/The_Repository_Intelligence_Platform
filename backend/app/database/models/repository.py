"""Repository ORM domain model for Repository Intelligence Platform.

Tracks persistent repository metadata and entity identity.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    RepositorySnapshot = Any


class Repository(Base, TimestampMixin):
    """Repository entity representing a tracked GitHub repository."""

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    github_repository_id: Mapped[int] = mapped_column(
        unique=True,
        index=True,
        nullable=False,
        comment="External unique numeric GitHub repository ID",
    )
    owner: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
        comment="Repository owner organization or user handle",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Repository name",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
        comment="Combined owner/name repository slug identifier",
    )
    default_branch: Mapped[str] = mapped_column(
        String(100),
        default="main",
        nullable=False,
        comment="Primary Git branch name",
    )
    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Primary programming language",
    )
    visibility: Mapped[str] = mapped_column(
        String(20),
        default="public",
        nullable=False,
        comment="Repository visibility scope (e.g. public, private)",
    )
    archived: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Flag indicating if repository is archived",
    )
    fork: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Flag indicating if repository is a fork",
    )

    # 1-to-many relationship with historical snapshots
    snapshots: Mapped[list["RepositorySnapshot"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        order_by="RepositorySnapshot.snapshot_time.desc()",
    )
