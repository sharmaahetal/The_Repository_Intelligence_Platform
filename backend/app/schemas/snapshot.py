"""Repository snapshot Pydantic schemas for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, Field

from backend.app.schemas.base import BaseSchema


class RepositorySnapshotCreate(BaseSchema):
    """Schema for creating a repository snapshot."""

    repository_id: int
    snapshot_time: datetime

    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0

    subscribers: int = 0
    network_count: int = 0
    size_kb: int = 0

    license: str | None = Field(default=None, validation_alias=AliasChoices("license", "license_name"))
    topics_json: dict[str, Any] | list[str] | None = None
    default_branch: str = "main"


class RepositorySnapshotUpdate(BaseSchema):
    """Schema for updating a repository snapshot."""

    stars: int | None = None
    forks: int | None = None
    watchers: int | None = None
    open_issues: int | None = None

    subscribers: int | None = None
    network_count: int | None = None
    size_kb: int | None = None

    license: str | None = Field(default=None, validation_alias=AliasChoices("license", "license_name"))
    topics_json: dict[str, Any] | list[str] | None = None
    default_branch: str | None = None


class RepositorySnapshotResponse(BaseSchema):
    """Repository snapshot response schema."""

    id: int
    repository_id: int
    snapshot_time: datetime

    stars: int
    forks: int
    watchers: int
    open_issues: int

    subscribers: int
    network_count: int
    size_kb: int

    license: str | None = Field(default=None, validation_alias=AliasChoices("license", "license_name"))
    topics_json: dict[str, Any] | list[str] | None = None
    default_branch: str = "main"

    collected_at: datetime
    created_at: datetime
    updated_at: datetime
