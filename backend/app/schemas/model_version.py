"""Model version Pydantic schemas for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime

from backend.app.schemas.base import BaseSchema


class ModelVersionCreate(BaseSchema):
    """Schema for registering a new model version."""

    version: str
    algorithm: str
    training_dataset_hash: str
    feature_schema_version: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc: float
    artifact_path: str
    trained_at: datetime
    training_duration_seconds: float | None = None
    cross_validation_score: float | None = None
    dataset_size: int | None = None
    random_seed: int | None = None
    git_commit_hash: str | None = None


class ModelVersionUpdate(BaseSchema):
    """Schema for updating model version attributes."""

    version: str | None = None
    algorithm: str | None = None
    training_dataset_hash: str | None = None
    feature_schema_version: str | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    auc: float | None = None
    artifact_path: str | None = None
    trained_at: datetime | None = None
    training_duration_seconds: float | None = None
    cross_validation_score: float | None = None
    dataset_size: int | None = None
    random_seed: int | None = None
    git_commit_hash: str | None = None


class ModelVersionResponse(BaseSchema):
    """Model version response schema."""

    id: int
    version: str
    algorithm: str
    training_dataset_hash: str
    feature_schema_version: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc: float
    artifact_path: str
    trained_at: datetime
    training_duration_seconds: float | None = None
    cross_validation_score: float | None = None
    dataset_size: int | None = None
    random_seed: int | None = None
    git_commit_hash: str | None = None
    created_at: datetime
    updated_at: datetime
