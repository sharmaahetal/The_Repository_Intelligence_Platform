from alembic.config import Config
from alembic.script import ScriptDirectory

from backend.app.core.settings import settings
from backend.app.database.base import ORM_METADATA


def test_alembic_config_script_location():
    """Verify alembic.ini points to backend/alembic directory and metadata is bound."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    assert script.dir.endswith("backend/alembic")
    assert ORM_METADATA is not None


def test_alembic_dynamic_url_binding():
    """Verify settings.database.url is accessible by alembic env configuration."""
    assert settings.database.url is not None
