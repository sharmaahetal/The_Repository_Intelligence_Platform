"""SQLAlchemy 2.0 Declarative Base and metadata configuration for Repository Intelligence Platform.

Provides a shared MetaData instance with deterministic naming conventions,
a modern DeclarativeBase root class, and a reusable TimestampMixin audit helper.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ============================================================================
# Step 2 — MetaData Naming Conventions for Deterministic Alembic Migrations
# ============================================================================

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


# ============================================================================
# Step 1 & 5 — Modern SQLAlchemy 2.0 Declarative Base Root
# ============================================================================

class Base(DeclarativeBase):
    """Declarative Base class for all ORM models."""

    metadata = metadata

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{col.name}={repr(getattr(self, col.name, None))}"
            for col in self.__table__.columns
        )
        return f"<{self.__class__.__name__}({fields})>"


# ============================================================================
# Step 4 — Reusable Timezone-Aware Audit Timestamp Mixin
# ============================================================================

class TimestampMixin:
    """Audit mixin providing created_at and updated_at timezone-aware timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
