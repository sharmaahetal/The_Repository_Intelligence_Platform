"""Repository Service implementing business logic rules for Repository entities."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models.repository import Repository
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.logging import logger
from backend.app.services.exceptions import (
    RepositoryAlreadyExists,
    RepositoryNotFound,
)


class RepositoryService:
    """Service layer enforcing domain business rules for GitHub repositories."""

    def __init__(
        self,
        uow: UnitOfWork | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        """Initialize RepositoryService with optional UnitOfWork or AsyncSession."""
        self.uow = uow
        self.session = session

    async def create_repository(
        self,
        *,
        owner: str,
        name: str,
        full_name: str,
        github_repository_id: int,
        default_branch: str = "main",
        language: str | None = None,
        visibility: str = "public",
        archived: bool = False,
        fork: bool = False,
    ) -> Repository:
        """Create a new GitHub repository after validating uniqueness."""
        if self.uow:
            async with self.uow as uow:
                if await uow.repositories.exists_by_full_name(full_name):
                    logger.warning(
                        "Repository creation rejected: full_name already exists",
                        extra={"full_name": full_name},
                    )
                    raise RepositoryAlreadyExists(full_name)

                existing_by_id = await uow.repositories.get_by_github_id(github_repository_id)
                if existing_by_id is not None:
                    logger.warning(
                        "Repository creation rejected: github_repository_id already exists",
                        extra={"github_repository_id": github_repository_id},
                    )
                    raise RepositoryAlreadyExists(github_repository_id)

                repo = await uow.repositories.create(
                    owner=owner,
                    name=name,
                    full_name=full_name,
                    github_repository_id=github_repository_id,
                    default_branch=default_branch,
                    language=language,
                    visibility=visibility,
                    archived=archived,
                    fork=fork,
                )
                logger.info("Successfully created repository entity", extra={"repository_id": repo.id})
                return repo
        else:
            async with UnitOfWork() as uow:
                if await uow.repositories.exists_by_full_name(full_name):
                    raise RepositoryAlreadyExists(full_name)

                existing_by_id = await uow.repositories.get_by_github_id(github_repository_id)
                if existing_by_id is not None:
                    raise RepositoryAlreadyExists(github_repository_id)

                return await uow.repositories.create(
                    owner=owner,
                    name=name,
                    full_name=full_name,
                    github_repository_id=github_repository_id,
                    default_branch=default_branch,
                    language=language,
                    visibility=visibility,
                    archived=archived,
                    fork=fork,
                )

    async def get_repository(
        self,
        *,
        repository_id: int | None = None,
        full_name: str | None = None,
        github_repository_id: int | None = None,
    ) -> Repository:
        """Retrieve a repository entity by ID, full name, or GitHub ID."""
        async with UnitOfWork() as uow:
            repo: Repository | None = None
            identifier: str | int = "unknown"

            if repository_id is not None:
                identifier = repository_id
                repo = await uow.repositories.get_by_id(repository_id)
            elif full_name is not None:
                identifier = full_name
                repo = await uow.repositories.get_by_full_name(full_name)
            elif github_repository_id is not None:
                identifier = github_repository_id
                repo = await uow.repositories.get_by_github_id(github_repository_id)

            if repo is None:
                raise RepositoryNotFound(identifier)
            return repo

    async def search(
        self,
        *,
        owner: str | None = None,
        language: str | None = None,
        visibility: str | None = None,
        archived: bool | None = None,
    ) -> list[Repository]:
        """Search repositories using domain filtering options."""
        async with UnitOfWork() as uow:
            return await uow.repositories.search(
                owner=owner,
                language=language,
                visibility=visibility,
                archived=archived,
            )

    async def update(
        self,
        repository_id: int,
        **attributes: Any,
    ) -> Repository:
        """Update an existing repository entity."""
        async with UnitOfWork() as uow:
            if not await uow.repositories.exists(repository_id):
                raise RepositoryNotFound(repository_id)

            updated = await uow.repositories.update(repository_id, attributes)
            if updated is None:
                raise RepositoryNotFound(repository_id)
            return updated

    async def delete(
        self,
        repository_id: int,
    ) -> bool:
        """Delete a repository entity."""
        async with UnitOfWork() as uow:
            if not await uow.repositories.exists(repository_id):
                raise RepositoryNotFound(repository_id)

            return await uow.repositories.delete(repository_id)
