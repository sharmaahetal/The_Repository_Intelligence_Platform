"""Database engine factory and lifecycle management for Repository Intelligence Platform.

Provides a shared AsyncEngine singleton, configuration factory, graceful shutdown,
and connection health checks.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text

from backend.app.core.settings import settings
from backend.app.logging import logger


# ============================================================================
# Section B & C — Engine Factory & Configuration Options
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

    engine_kwargs: dict[str, Any] = {
        "echo": settings.database.echo,
    }

    if is_sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_size"] = settings.database.pool_size
        engine_kwargs["max_overflow"] = settings.database.max_overflow
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_recycle"] = 1800

    return create_async_engine(target_url, **engine_kwargs)


# ============================================================================
# Section E — Engine Singleton Instance
# ============================================================================

engine: AsyncEngine = create_engine()


# ============================================================================
# Section F — Graceful Shutdown Lifecycle
# ============================================================================

async def dispose_engine() -> None:
    """Gracefully close and dispose of pooled database engine connections during shutdown."""
    logger.info("Disposing database engine connection pool...")
    await engine.dispose()
    logger.info("Database engine connections disposed successfully.")


# ============================================================================
# Section G — Health Check Probe
# ============================================================================

async def check_database_connection() -> bool:
    """Verify database connectivity by executing a lightweight SELECT 1 query.

    Returns:
        True if the database responds successfully, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as exc:
        logger.error(f"Database connection health check failed: {exc}")
        return False
