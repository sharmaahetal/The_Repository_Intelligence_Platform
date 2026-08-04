"""Repository entity repository for Repository Intelligence Platform."""

from __future__ import annotations

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.repository import Repository
from backend.app.database.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    """Strongly typed repository for managing Repository entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize RepositoryRepository with session and Repository model."""
        super().__init__(session, Repository)

    async def get_by_full_name(self, full_name: str) -> Repository | None:
        """Retrieve a repository entity by its full_name slug (e.g. 'openai/gym')."""
        statement = select(Repository).where(Repository.full_name == full_name)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_github_id(self, github_repository_id: int) -> Repository | None:
        """Retrieve a repository entity by its numeric GitHub ID."""
        statement = select(Repository).where(Repository.github_repository_id == github_repository_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def exists_by_full_name(self, full_name: str) -> bool:
        """Check if a repository with full_name slug exists."""
        statement = select(exists().where(Repository.full_name == full_name))
        result = await self.session.execute(statement)
        return bool(result.scalar())

    async def search(
        self,
        owner: str | None = None,
        language: str | None = None,
        visibility: str | None = None,
        archived: bool | None = None,
    ) -> list[Repository]:
        """Search repositories using composable query construction across metadata filters."""
        statement = select(Repository)

        if owner is not None:
            statement = statement.where(Repository.owner == owner)
        if language is not None:
            statement = statement.where(Repository.language == language)
        if visibility is not None:
            statement = statement.where(Repository.visibility == visibility)
        if archived is not None:
            statement = statement.where(Repository.archived == archived)

        result = await self.session.execute(statement)
        return list(result.scalars().all())
