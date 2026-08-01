from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class RawRepositoryPayload(BaseModel):
    """Pydantic model validating raw GitHub repository API payload."""

    model_config = ConfigDict(extra="allow")

    name: str
    owner: dict[str, Any] | str
    full_name: str | None = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    subscribers_count: int = 0
    size: int = 0
    language: str | None = "Unknown"
    default_branch: str = "main"
    has_wiki: bool = False
    has_pages: bool = False
    pushed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @property
    def owner_login(self) -> str:
        """Helper to safely retrieve owner login handle."""
        if isinstance(self.owner, dict):
            return self.owner.get("login", "")
        return str(self.owner)
