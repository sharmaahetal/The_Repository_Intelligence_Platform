"""Prediction explanation ORM domain model for Repository Intelligence Platform.

Stores SHAP feature importance breakdowns and narrative summaries for predictions.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.database.models.prediction import Prediction


class PredictionExplanation(Base, TimestampMixin):
    """Prediction explanation entity storing SHAP feature importance output."""

    __tablename__ = "prediction_explanations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(
        nullable=False,
        comment="Human-readable prediction narrative summary",
    )
    top_positive_features: Mapped[dict[str, Any] | list[Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Top positive feature contributions",
    )
    top_negative_features: Mapped[dict[str, Any] | list[Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Top negative feature contributions",
    )
    shap_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Full SHAP feature importance dictionary mapping",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    prediction: Mapped["Prediction"] = relationship(
        back_populates="explanation",
    )
