"""Prediction explanation Pydantic schemas for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.schemas.base import BaseSchema


class PredictionExplanationCreate(BaseSchema):
    """Schema for creating a prediction explanation."""

    prediction_id: int
    summary: str
    top_positive_features: dict[str, Any]
    top_negative_features: dict[str, Any]
    shap_json: dict[str, Any]


class PredictionExplanationUpdate(BaseSchema):
    """Schema for updating a prediction explanation."""

    summary: str | None = None
    top_positive_features: dict[str, Any] | None = None
    top_negative_features: dict[str, Any] | None = None
    shap_json: dict[str, Any] | None = None


class PredictionExplanationResponse(BaseSchema):
    """Prediction explanation response schema."""

    id: int
    prediction_id: int
    summary: str
    top_positive_features: dict[str, Any]
    top_negative_features: dict[str, Any]
    shap_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
