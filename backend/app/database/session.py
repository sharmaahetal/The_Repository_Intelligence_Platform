"""Database session lifecycle and dependency management for Repository Intelligence Platform.

Provides lazy session factory initialization, transaction rollback handling,
and FastAPI dependency injection generator.
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database.engine import get_engine
from backend.app.logging import logger

_sessionmaker: async_sessionmaker[AsyncSession] | None = None


# ============================================================================
# Step 1 — Session Factory Initialization (Lazy Singleton)
# ============================================================================

def create_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Create a new async_sessionmaker factory bound to the shared engine."""
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Retrieve or lazily initialize the shared async_sessionmaker factory singleton."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = create_sessionmaker()
    return _sessionmaker


class LazySessionFactoryProxy:
    """Proxy object allowing `SessionFactory()` or `AsyncSessionLocal()` factory invocations."""

    def __call__(self, *args: Any, **kwargs: Any) -> AsyncSession:
        return get_session_factory()(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(get_session_factory(), name)


SessionFactory: Any = LazySessionFactoryProxy()
AsyncSessionLocal: Any = SessionFactory


# ============================================================================
# Step 2 & 3 — FastAPI Dependency Generator & Transaction Rollback Handling
# ============================================================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a managed AsyncSession with automatic transaction rollback and closure.

    Yields:
        AsyncSession instance.
    """
    factory = get_session_factory()
    session: AsyncSession = factory()
    logger.debug("Database session created", extra={"component": "db_session"})

    try:
        yield session
    except Exception as exc:
        logger.exception(
            "Transaction error occurred during database session execution, rolling back",
            extra={"component": "db_session", "error_type": type(exc).__name__},
        )
        await session.rollback()
        raise
    finally:
        await session.close()
        logger.debug("Database session closed", extra={"component": "db_session"})
