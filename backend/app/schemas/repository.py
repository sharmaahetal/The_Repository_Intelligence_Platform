"""Repository Pydantic schemas for Repository Intelligence Platform."""

from __future__ import annotations

from datetime import datetime

from backend.app.schemas.base import BaseSchema


class RepositoryCreate(BaseSchema):
    """Schema for creating a repository."""

    github_repository_id: int
    owner: str
    name: str
    full_name: str
    default_branch: str = "main"
    language: str | None = None
    visibility: str = "public"
    archived: bool = False
    fork: bool = False


class RepositoryUpdate(BaseSchema):
    """Schema for updating a repository."""

    owner: str | None = None
    name: str | None = None
    full_name: str | None = None
    default_branch: str | None = None
    language: str | None = None
    visibility: str | None = None
    archived: bool | None = None
    fork: bool | None = None


class RepositoryResponse(BaseSchema):
    """Repository response schema."""

    id: int
    github_repository_id: int
    owner: str
    name: str
    full_name: str
    default_branch: str
    language: str | None
    visibility: str
    archived: bool
    fork: bool
    created_at: datetime
    updated_at: datetime


class RepositorySearch(BaseSchema):
    """Repository search filter schema."""

    owner: str | None = None
    language: str | None = None
    visibility: str | None = None
    archived: bool | None = None
