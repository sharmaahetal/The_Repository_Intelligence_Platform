"""API package for Repository Intelligence Platform."""

from backend.app.api.forecast import router as forecast_router
from backend.app.api.health import router as health_router
from backend.app.api.router import router

__all__ = [
    "health_router",
    "forecast_router",
    "router",
]
