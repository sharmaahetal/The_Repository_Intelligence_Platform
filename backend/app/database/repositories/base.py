"""Generic Async Base Repository for Repository Intelligence Platform.

Provides reusable asynchronous CRUD data access operations across all ORM models.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.base import Base
from backend.app.logging import logger

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository encapsulating common ORM database operations."""

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        """Initialize the repository with a database session and target ORM model."""
        self.session = session
        self.model = model

    async def create(self, **attributes: Any) -> T:
        """Construct, persist to session, flush, refresh, and return a new ORM instance."""
        instance = self.model(**attributes)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        logger.info(
            "Created entity",
            extra={
                "component": "db_repository",
                "model": self.model.__name__,
            },
        )
        return instance

    async def bulk_create(self, objects: list[dict[str, Any]]) -> list[T]:
        """Construct, persist, flush, refresh, and return multiple ORM instances."""
        if not objects:
            return []

        instances = [self.model(**obj) for obj in objects]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)

        logger.info(
            "Bulk created entities",
            extra={
                "component": "db_repository",
                "model": self.model.__name__,
                "count": len(instances),
            },
        )
        return instances

    async def get(self, **filters: Any) -> T | None:
        """Retrieve a single ORM entity matching keyword filter criteria."""
        statement = select(self.model).filter_by(**filters)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, entity_id: int) -> T | None:
        """Retrieve an ORM entity by its primary key identifier."""
        statement = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[T]:
        """Retrieve all entity rows for the model."""
        statement = select(self.model)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list(self) -> list[T]:
        """Retrieve all entity rows for the model (alias for list_all)."""
        return await self.list_all()

    async def update(self, entity_id: int, attributes: dict[str, Any]) -> T | None:
        """Update specified attributes on an existing entity with field validation."""
        instance = await self.get_by_id(entity_id)
        if instance is None:
            return None

        for key in attributes:
            if not hasattr(instance, key):
                raise ValueError(f"Unknown attribute '{key}' for model '{self.model.__name__}'")

        for key, value in attributes.items():
            setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        logger.info(
            "Updated entity",
            extra={
                "component": "db_repository",
                "model": self.model.__name__,
                "entity_id": entity_id,
                "updated_keys": list(attributes.keys()),
            },
        )
        return instance

    async def delete(self, entity_id: int) -> bool:
        """Delete an entity by its primary key identifier."""
        statement = delete(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
        result = await self.session.execute(statement)
        await self.session.flush()
        deleted = (getattr(result, "rowcount", 0) or 0) > 0
        if deleted:
            logger.info(
                "Deleted entity",
                extra={
                    "component": "db_repository",
                    "model": self.model.__name__,
                    "entity_id": entity_id,
                },
            )
        return deleted

    async def exists(self, entity_id: int) -> bool:
        """Check if an entity exists by primary key identifier using optimized EXISTS clause."""
        statement = select(exists().where(self.model.id == entity_id))  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
        result = await self.session.execute(statement)
        return bool(result.scalar())

    async def count(self) -> int:
        """Return the total number of entity rows."""
        statement = select(func.count(1)).select_from(self.model)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() or 0

    async def refresh(self, instance: T) -> None:
        """Refresh the attributes of the given ORM instance from the database."""
        await self.session.refresh(instance)

    async def flush(self) -> None:
        """Flush pending changes from the session to the database."""
        await self.session.flush()
