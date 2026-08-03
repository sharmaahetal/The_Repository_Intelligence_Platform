import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.app.database.engine import (
    check_database_connection,
    create_engine,
    dispose_engine,
    get_engine,
)


@pytest.mark.asyncio
async def test_lazy_engine_initialization():
    """Verify get_engine lazily initializes the AsyncEngine singleton."""
    eng1 = get_engine()
    eng2 = get_engine()
    assert isinstance(eng1, AsyncEngine)
    assert eng1 is eng2


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
    """Verify dispose_engine runs without errors and clears singleton."""
    await dispose_engine()
    # Next get_engine call will recreate lazily
    eng = get_engine()
    assert isinstance(eng, AsyncEngine)
    await dispose_engine()
