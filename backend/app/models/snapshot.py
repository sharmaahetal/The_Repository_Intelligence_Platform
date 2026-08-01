from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RepositorySnapshot(BaseModel):
    """Pydantic immutable model representing point-in-time repository snapshot S(t_k)."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    schema_version: int = Field(default=1, frozen=True)
    snapshot_timestamp: datetime
    owner: str
    name: str
    full_name: str
    stars_count: int = Field(default=0)
    forks_count: int = Field(default=0)
    open_issues_count: int = Field(default=0)
    subscribers_count: int = Field(default=0)
    size_kb: int = Field(default=0)
    primary_language: str = Field(default="Unknown")
    default_branch: str = Field(default="main")
    has_wiki: bool = Field(default=False)
    has_pages: bool = Field(default=False)
    pushed_at: str | datetime | None = None
    created_at: str | datetime | None = None
    updated_at: str | datetime | None = None
