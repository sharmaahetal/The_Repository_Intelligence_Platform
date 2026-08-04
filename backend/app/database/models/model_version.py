"""Model version ORM domain model for Repository Intelligence Platform.

Tracks ML model registry versions, hyperparameters, dataset hashes, and evaluation metrics.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.database.models.prediction import Prediction


class ModelVersion(Base, TimestampMixin):
    """Model version entity tracking trained ML models, performance metrics, and artifacts."""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(
        unique=True,
        index=True,
        nullable=False,
        comment="Semantic model version string (e.g. v1.2.0)",
    )
    algorithm: Mapped[str] = mapped_column(
        nullable=False,
        comment="Machine learning algorithm implementation (e.g. xgboost)",
    )
    training_dataset_hash: Mapped[str] = mapped_column(
        nullable=False,
        comment="SHA-256 hash of the dataset used for model training",
    )
    feature_schema_version: Mapped[str] = mapped_column(
        nullable=False,
        comment="Version of the feature engineering schema",
    )
    accuracy: Mapped[float] = mapped_column(nullable=False)
    precision: Mapped[float] = mapped_column(nullable=False)
    recall: Mapped[float] = mapped_column(nullable=False)
    f1: Mapped[float] = mapped_column(nullable=False)
    auc: Mapped[float] = mapped_column(nullable=False)
    artifact_path: Mapped[str] = mapped_column(
        nullable=False,
        comment="Filesystem path to model artifact file",
    )
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when model training completed",
    )

    # Relationships
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="model_version",
    )

    __table_args__ = (
        CheckConstraint("accuracy >= 0 AND accuracy <= 1", name="accuracy_range"),
        CheckConstraint("precision >= 0 AND precision <= 1", name="precision_range"),
        CheckConstraint("recall >= 0 AND recall <= 1", name="recall_range"),
        CheckConstraint("f1 >= 0 AND f1 <= 1", name="f1_range"),
        CheckConstraint("auc >= 0 AND auc <= 1", name="auc_range"),
    )

