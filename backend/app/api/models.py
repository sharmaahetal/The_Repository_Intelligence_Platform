from datetime import UTC, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class TopFactor(BaseModel):
    """Represents a single top factor/driver in forecast explanation."""

    model_config = ConfigDict(frozen=True)

    name: str
    impact: float
    description: str


class ForecastDetails(BaseModel):
    """Structured breakdown of predicted probabilities and health index."""

    model_config = ConfigDict(frozen=True)

    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float
    derived_health_index: int


class ForecastResponse(BaseModel):
    """Production-grade structured forecast response payload."""

    model_config = ConfigDict(frozen=True)

    repository: str
    owner: str
    repo: str
    prediction_horizon_days: int
    prediction_time: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    snapshot_time: str
    model_version: str = Field(default="v1.0")
    feature_schema_version: int = Field(default=1)
    label_schema_version: int = Field(default=1)

    forecast: ForecastDetails
    confidence: float
    top_factors: list[TopFactor] = Field(default_factory=list)
    narrative_summary: str
    top_drivers: list[str] = Field(default_factory=list)
    top_risks: list[str] = Field(default_factory=list)

    cached: bool = Field(default=False)


class HealthResponse(BaseModel):
    """Liveness probe health check response payload."""

    model_config = ConfigDict(frozen=True)

    status: str = Field(default="ok")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: str = Field(default="1.0.0")


class ReadinessResponse(BaseModel):
    """Readiness probe response verifying memory model loading and infrastructure components."""

    model_config = ConfigDict(frozen=True)

    status: str = Field(default="ready")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    model_loaded: bool
    registry_available: bool
    snapshot_service_ready: bool
    details: dict[str, Any] = Field(default_factory=dict)
