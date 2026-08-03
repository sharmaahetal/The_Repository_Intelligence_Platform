import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.app.database.engine import (
    check_database_connection,
    create_engine,
    dispose_engine,
    engine,
)


@pytest.mark.asyncio
async def test_engine_singleton_instance():
    """Verify shared engine singleton is an AsyncEngine instance."""
    assert isinstance(engine, AsyncEngine)


@pytest.mark.asyncio
async def test_create_engine_factory():
    """Verify engine factory creates custom engine instances."""
    custom_engine = create_engine("sqlite+aiosqlite:///:memory:")
    assert isinstance(custom_engine, AsyncEngine)
    await custom_engine.dispose()


@pytest.mark.asyncio
async def test_check_database_connection_success():
    """Verify check_database_connection executes SELECT 1 and returns True."""
    result = await check_database_connection()
    assert result is True


@pytest.mark.asyncio
async def test_dispose_engine_cleanly():
    """Verify dispose_engine runs without errors or unhandled warnings."""
    await dispose_engine()
