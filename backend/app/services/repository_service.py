"""Repository Service implementing business logic rules for Repository entities."""

from __future__ import annotations

from typing import Any

from backend.app.database.models.repository import Repository
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.logging import logger
from backend.app.services.exceptions import (
    RepositoryAlreadyExists,
    RepositoryNotFound,
)


class RepositoryService:
    """Service layer enforcing domain business rules for GitHub repositories."""

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        """Initialize RepositoryService with optional injected UnitOfWork context."""
        self.uow = uow

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
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            if await uow.repositories.exists_by_full_name(full_name):
                logger.warning(
                    "Repository creation rejected: full_name already exists",
                    extra={"repository": full_name},
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
            await uow.commit()
            logger.info(
                "Repository created", extra={"repository": full_name, "repository_id": repo.id}
            )
            return repo

    async def get_repository(
        self,
        *,
        repository_id: int | None = None,
        full_name: str | None = None,
        github_repository_id: int | None = None,
    ) -> Repository:
        """Retrieve a repository entity by ID, full name, or GitHub ID."""
        if repository_id is None and full_name is None and github_repository_id is None:
            raise ValueError(
                "At least one lookup identifier (repository_id, full_name, or github_repository_id) must be provided."
            )

        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
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

    async def update_repository(
        self,
        repository_id: int,
        **attributes: Any,
    ) -> Repository:
        """Update an existing repository entity."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            updated = await uow.repositories.update(repository_id, attributes)
            if updated is None:
                raise RepositoryNotFound(repository_id)

            await uow.commit()
            logger.info("Repository updated", extra={"repository_id": repository_id})
            return updated

    async def delete_repository(
        self,
        repository_id: int,
    ) -> bool:
        """Delete a repository entity."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            deleted = await uow.repositories.delete(repository_id)
            if not deleted:
                raise RepositoryNotFound(repository_id)

            await uow.commit()
            logger.info("Repository deleted", extra={"repository_id": repository_id})
            return True

    async def search_repositories(
        self,
        *,
        owner: str | None = None,
        language: str | None = None,
        visibility: str | None = None,
        archived: bool | None = None,
    ) -> list[Repository]:
        """Search repositories using domain filtering criteria."""
        uow_context = self.uow if self.uow is not None else UnitOfWork()
        async with uow_context as uow:
            return await uow.repositories.search(
                owner=owner,
                language=language,
                visibility=visibility,
                archived=archived,
            )
