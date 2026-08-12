"""Core settings compatibility module re-exporting canonical settings from backend.app.config."""

from backend.app.config import settings
from backend.app.config.settings import Settings

__all__ = [
    "settings",
    "Settings",
]
