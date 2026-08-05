"""Prediction Pydantic schemas for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime

from backend.app.schemas.base import BaseSchema


class PredictionCreate(BaseSchema):
    """Schema for creating a prediction."""

    repository_snapshot_id: int
    model_version_id: int
    predicted_growth: float
    confidence: float
    prediction_timestamp: datetime
    prediction_horizon_days: int = 30


class PredictionUpdate(BaseSchema):
    """Schema for updating a prediction."""

    predicted_growth: float | None = None
    confidence: float | None = None
    prediction_timestamp: datetime | None = None
    prediction_horizon_days: int | None = None


class PredictionResponse(BaseSchema):
    """Prediction response schema."""

    id: int
    repository_snapshot_id: int
    model_version_id: int
    predicted_growth: float
    confidence: float
    prediction_timestamp: datetime
    prediction_horizon_days: int
    created_at: datetime
    updated_at: datetime
