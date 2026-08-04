"""Prediction ORM domain model for Repository Intelligence Platform.

Tracks ML inference output predictions linked to repository snapshots and model versions.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.database.models.explanation import PredictionExplanation
    from backend.app.database.models.model_version import ModelVersion
    from backend.app.database.models.snapshot import RepositorySnapshot


class Prediction(Base, TimestampMixin):
    """Prediction entity representing model inference results for a snapshot."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repository_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("repository_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_version_id: Mapped[int] = mapped_column(
        ForeignKey("model_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    predicted_growth: Mapped[float] = mapped_column(
        nullable=False,
        comment="Predicted repository growth metric delta/rate",
    )
    confidence: Mapped[float] = mapped_column(
        nullable=False,
        comment="Prediction confidence score between 0 and 1",
    )
    prediction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when prediction was calculated",
    )
    prediction_horizon_days: Mapped[int] = mapped_column(
        default=30,
        nullable=False,
        comment="Prediction forecast horizon window in days",
    )

    # Relationships
    snapshot: Mapped["RepositorySnapshot"] = relationship(
        back_populates="predictions",
    )
    model_version: Mapped["ModelVersion"] = relationship(
        back_populates="predictions",
    )
    explanation: Mapped["PredictionExplanation | None"] = relationship(
        back_populates="prediction",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_predictions_created_at", "created_at"),
        UniqueConstraint(
            "repository_snapshot_id",
            "model_version_id",
            "prediction_horizon_days",
            name="prediction_model_snapshot_horizon",
        ),
        CheckConstraint("prediction_horizon_days > 0", name="horizon_positive"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
    )
