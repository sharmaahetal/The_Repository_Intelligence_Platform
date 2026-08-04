"""Repository-specific data access layer for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.repository import Repository
from backend.app.database.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    """Repository-specific data access layer."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize RepositoryRepository with session and Repository model."""
        super().__init__(session, Repository)

    async def get_by_full_name(self, full_name: str) -> Repository | None:
        """Return a repository using owner/name slug."""
        stmt = select(Repository).where(Repository.full_name == full_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_github_id(
        self,
        github_repository_id: int,
    ) -> Repository | None:
        """Return a repository using GitHub numeric ID."""
        stmt = select(Repository).where(Repository.github_repository_id == github_repository_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_full_name(self, full_name: str) -> bool:
        """Check if a repository with owner/name full_name slug exists."""
        repo = await self.get_by_full_name(full_name)
        return repo is not None

    async def search(
        self,
        *,
        owner: str | None = None,
        language: str | None = None,
        visibility: str | None = None,
        archived: bool | None = None,
    ) -> list[Repository]:
        """Search repositories using composable query construction across metadata filters."""
        stmt = select(Repository)

        if owner is not None:
            stmt = stmt.where(Repository.owner == owner)
        if language is not None:
            stmt = stmt.where(Repository.language == language)
        if visibility is not None:
            stmt = stmt.where(Repository.visibility == visibility)
        if archived is not None:
            stmt = stmt.where(Repository.archived == archived)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
