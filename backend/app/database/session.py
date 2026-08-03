"""Database session lifecycle and dependency management for Repository Intelligence Platform.

Provides session factory initialization, transaction rollback handling,
and FastAPI dependency injection generator.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database.engine import get_engine
from backend.app.logging import logger


# ============================================================================
# Step 1 — Session Factory Initialization
# ============================================================================

def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Retrieve or create an async_sessionmaker factory bound to the shared engine."""
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


AsyncSessionLocal: async_sessionmaker[AsyncSession] = get_sessionmaker()


# ============================================================================
# Step 2 & 3 — FastAPI Dependency Generator & Transaction Rollback Handling
# ============================================================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a managed AsyncSession with automatic transaction rollback and closure.

    Yields:
        AsyncSession instance.
    """
    session_factory = get_sessionmaker()
    session: AsyncSession = session_factory()
    logger.debug("Database session created.")

    try:
        yield session
    except Exception as exc:
        logger.exception(
            "Transaction error occurred during database session execution, rolling back",
            extra={"error_type": type(exc).__name__},
        )
        await session.rollback()
        raise
    finally:
        await session.close()
        logger.debug("Database session closed.")
