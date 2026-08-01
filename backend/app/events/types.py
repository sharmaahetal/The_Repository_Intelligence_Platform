from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class Event:
    """Base immutable event object."""

    event_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class RepositoryCollectedEvent(Event):
    """Event emitted when raw payload is collected from GitHub API."""

    owner: str = ""
    repo: str = ""
    payload_hash: str = ""


@dataclass(frozen=True)
class SnapshotCreatedEvent(Event):
    """Event emitted when a RepositorySnapshot S(t) is deterministically built."""

    full_name: str = ""
    stars_count: int = 0
    forks_count: int = 0


@dataclass(frozen=True)
class FeaturesComputedEvent(Event):
    """Event emitted when RepositoryFeatures vector is calculated."""

    full_name: str = ""
    num_features: int = 0
    schema_version: int = 1


@dataclass(frozen=True)
class ModelTrainedEvent(Event):
    """Event emitted when XGBoost growth model training completes."""

    model_name: str = ""
    model_version: str = ""
    roc_auc: float = 0.0


@dataclass(frozen=True)
class DriftDetectedEvent(Event):
    """Event emitted when PSI feature or prediction drift is detected."""

    feature_name: str = ""
    psi_value: float = 0.0
    severity: str = "stable"
