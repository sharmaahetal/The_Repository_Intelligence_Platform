"""SQLAlchemy 2.0 Declarative Base and metadata configuration for Repository Intelligence Platform.

Provides a shared MetaData instance with deterministic naming conventions,
a modern DeclarativeBase root class with concise repr, and a reusable TimestampMixin audit helper.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ============================================================================
# Step 2 — MetaData Naming Conventions for Deterministic Alembic Migrations
# ============================================================================

POSTGRES_NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

ORM_METADATA: MetaData = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)

# Backwards compatibility aliases
metadata: MetaData = ORM_METADATA
NAMING_CONVENTION: dict[str, str] = POSTGRES_NAMING_CONVENTION


# ============================================================================
# Step 1 & 5 — Modern SQLAlchemy 2.0 Declarative Base Root
# ============================================================================

class Base(DeclarativeBase):
    """Declarative Base class for all ORM models."""

    metadata = ORM_METADATA

    def __repr__(self) -> str:
        """Concise string representation displaying primary key or class name."""
        pk_val = getattr(self, "id", None)
        if pk_val is not None:
            return f"<{self.__class__.__name__}(id={pk_val!r})>"
        return f"<{self.__class__.__name__}()>"


# ============================================================================
# Step 4 — Reusable Timezone-Aware Audit Timestamp Mixin
# ============================================================================

class TimestampMixin:
    """Abstract audit mixin providing created_at and updated_at timezone-aware timestamps.

    Intended for inheritance alongside Base by domain ORM models.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
