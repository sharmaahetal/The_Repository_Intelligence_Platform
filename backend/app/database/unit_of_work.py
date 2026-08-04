"""Unit of Work implementation for Repository Intelligence Platform.

Coordinates atomic database transactions and manages repository access across a shared AsyncSession.
"""

from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database.repositories.explanation import PredictionExplanationRepository
from backend.app.database.repositories.model_version import ModelVersionRepository
from backend.app.database.repositories.prediction import PredictionRepository
from backend.app.database.repositories.repository import RepositoryRepository
from backend.app.database.repositories.snapshot import SnapshotRepository
from backend.app.database.session import AsyncSessionLocal
from backend.app.logging import logger


class UnitOfWork:
    """Unit of Work managing transaction context and entity repositories sharing a single AsyncSession."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] | None = None) -> None:
        """Initialize UnitOfWork with session factory."""
        self.session_factory = session_factory or AsyncSessionLocal
        self.session: AsyncSession | None = None
        self._repositories: RepositoryRepository | None = None
        self._snapshots: SnapshotRepository | None = None
        self._predictions: PredictionRepository | None = None
        self._model_versions: ModelVersionRepository | None = None
        self._explanations: PredictionExplanationRepository | None = None

    @property
    def repositories(self) -> RepositoryRepository:
        """RepositoryRepository instance for the current session."""
        if self._repositories is None or self.session is None:
            raise RuntimeError("UnitOfWork context has not been entered.")
        return self._repositories

    @property
    def snapshots(self) -> SnapshotRepository:
        """SnapshotRepository instance for the current session."""
        if self._snapshots is None or self.session is None:
            raise RuntimeError("UnitOfWork context has not been entered.")
        return self._snapshots

    @property
    def predictions(self) -> PredictionRepository:
        """PredictionRepository instance for the current session."""
        if self._predictions is None or self.session is None:
            raise RuntimeError("UnitOfWork context has not been entered.")
        return self._predictions

    @property
    def model_versions(self) -> ModelVersionRepository:
        """ModelVersionRepository instance for the current session."""
        if self._model_versions is None or self.session is None:
            raise RuntimeError("UnitOfWork context has not been entered.")
        return self._model_versions

    @property
    def explanations(self) -> PredictionExplanationRepository:
        """PredictionExplanationRepository instance for the current session."""
        if self._explanations is None or self.session is None:
            raise RuntimeError("UnitOfWork context has not been entered.")
        return self._explanations

    async def __aenter__(self) -> Self:
        """Enter transaction context: instantiate AsyncSession and entity repositories."""
        self.session = self.session_factory()
        self._repositories = RepositoryRepository(self.session)
        self._snapshots = SnapshotRepository(self.session)
        self._predictions = PredictionRepository(self.session)
        self._model_versions = ModelVersionRepository(self.session)
        self._explanations = PredictionExplanationRepository(self.session)
        logger.debug("Entered UnitOfWork context", extra={"component": "unit_of_work"})
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit transaction context: rollback on exception, commit otherwise, and close session."""
        try:
            if exc_val is not None:
                logger.warning(
                    "Error inside UnitOfWork context, triggering transaction rollback",
                    extra={"component": "unit_of_work", "error_type": exc_type.__name__ if exc_type else "None"},
                )
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.close()
            logger.debug("Exited UnitOfWork context", extra={"component": "unit_of_work"})

    async def commit(self) -> None:
        """Commit current transaction changes to the database."""
        if self.session is not None:
            await self.session.commit()
            logger.debug("Committed UnitOfWork transaction", extra={"component": "unit_of_work"})

    async def rollback(self) -> None:
        """Roll back current transaction changes."""
        if self.session is not None:
            await self.session.rollback()
            logger.debug("Rolled back UnitOfWork transaction", extra={"component": "unit_of_work"})

    async def flush(self) -> None:
        """Flush pending changes to the database without committing the transaction."""
        if self.session is not None:
            await self.session.flush()
            logger.debug("Flushed UnitOfWork session state", extra={"component": "unit_of_work"})

    async def close(self) -> None:
        """Close the active AsyncSession."""
        if self.session is not None:
            await self.session.close()
            self.session = None
            logger.debug("Closed UnitOfWork session", extra={"component": "unit_of_work"})
