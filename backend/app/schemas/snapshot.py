"""Repository snapshot Pydantic schemas for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, Field

from backend.app.schemas.base import BaseSchema


class RepositorySnapshotCreate(BaseSchema):
    """Schema for creating a repository snapshot."""

    repository_id: int
    snapshot_time: datetime

    stars: int
    forks: int
    watchers: int
    open_issues: int

    subscribers: int
    network_count: int
    size_kb: int

    primary_language: str | None = None
    license_name: str | None = Field(default=None, validation_alias=AliasChoices("license_name", "license"))


class RepositorySnapshotUpdate(BaseSchema):
    """Schema for updating a repository snapshot."""

    stars: int | None = None
    forks: int | None = None
    watchers: int | None = None
    open_issues: int | None = None

    subscribers: int | None = None
    network_count: int | None = None
    size_kb: int | None = None

    primary_language: str | None = None
    license_name: str | None = Field(default=None, validation_alias=AliasChoices("license_name", "license"))


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

    primary_language: str | None = None
    license_name: str | None = Field(default=None, validation_alias=AliasChoices("license_name", "license"))

    created_at: datetime
    updated_at: datetime
