"""Database engine factory and lifecycle management for Repository Intelligence Platform.

Provides a shared AsyncEngine singleton via lazy initialization, engine factory,
graceful shutdown, and connection health checks.
"""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text

from backend.app.config import settings
from backend.app.logging import logger

EngineOptions = dict[str, Any]

_engine: AsyncEngine | None = None


# ============================================================================
# Engine Factory & Options Configuration
# ============================================================================

def create_engine(database_url: str | None = None) -> AsyncEngine:
    """Create and configure an AsyncEngine instance with production connection pool options.

    Args:
        database_url: Optional database connection string override. If omitted,
                      reads configuration from settings.database.url.

    Returns:
        Configured AsyncEngine instance.
    """
    target_url = database_url or settings.database.url
    is_sqlite = target_url.startswith("sqlite")

    engine_kwargs: EngineOptions = {
        "echo": settings.database.echo,
    }

    if is_sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        logger.info(
            "Creating async database engine",
            extra={
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow,
                "pool_timeout": settings.database.pool_timeout,
                "pool_recycle": settings.database.pool_recycle,
                "pool_use_lifo": settings.database.pool_use_lifo,
            },
        )
        engine_kwargs["pool_size"] = settings.database.pool_size
        engine_kwargs["max_overflow"] = settings.database.max_overflow
        engine_kwargs["pool_timeout"] = settings.database.pool_timeout
        engine_kwargs["pool_recycle"] = settings.database.pool_recycle
        engine_kwargs["pool_use_lifo"] = settings.database.pool_use_lifo
        engine_kwargs["pool_pre_ping"] = True

    return create_async_engine(target_url, **engine_kwargs)


# ============================================================================
# Lazy Initialization Engine Accessor
# ============================================================================

def get_engine(database_url: str | None = None) -> AsyncEngine:
    """Retrieve or lazily initialize the shared AsyncEngine singleton instance.

    Args:
        database_url: Optional database URL override for custom engine instances.

    Returns:
        The AsyncEngine instance.
    """
    global _engine
    if database_url is not None:
        return create_engine(database_url)
    if _engine is None:
        _engine = create_engine()
    return _engine


class LazyEngineProxy:
    """Proxy object allowing `from backend.app.database.engine import engine` backward compatibility."""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_engine(), name)


engine: Any = LazyEngineProxy()


# ============================================================================
# Graceful Shutdown Lifecycle
# ============================================================================

async def dispose_engine() -> None:
    """Gracefully close and dispose of pooled database engine connections during shutdown."""
    global _engine
    if _engine is not None:
        logger.info("Disposing database engine connection pool...")
        await _engine.dispose()
        _engine = None
        logger.info("Database engine connections disposed successfully.")


# ============================================================================
# Health Check Probe
# ============================================================================

async def check_database_connection() -> bool:
    """Verify database connectivity by executing a lightweight SELECT 1 query.

    Returns:
        True if the database responds successfully, False otherwise.
    """
    eng = get_engine()
    try:
        async with eng.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError:
        logger.exception(
            "Database health check failed",
            extra={"database_url": settings.database.url},
        )
        return False
