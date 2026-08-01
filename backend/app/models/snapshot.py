from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class RepositorySnapshot(BaseModel):
    """Pydantic model representing point-in-time repository snapshot S(t_k)."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    snapshot_timestamp: datetime
    owner: str
    name: str
    full_name: str
    stars_count: int = Field(default=0, alias="stars_count")
    forks_count: int = Field(default=0, alias="forks_count")
    open_issues_count: int = Field(default=0, alias="open_issues_count")
    subscribers_count: int = Field(default=0, alias="subscribers_count")
    size_kb: int = Field(default=0, alias="size_kb")
    primary_language: str = Field(default="Unknown", alias="primary_language")
    default_branch: str = Field(default="main", alias="default_branch")
    has_wiki: bool = Field(default=False, alias="has_wiki")
    has_pages: bool = Field(default=False, alias="has_pages")
    pushed_at: str | datetime | None = None
    created_at: str | datetime | None = None
    updated_at: str | datetime | None = None

    def get(self, key: str, default: Any = None) -> Any:
        """Provide dictionary-like get accessor for backwards compatibility."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Provide dictionary-like subscript accessor for backwards compatibility."""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)
