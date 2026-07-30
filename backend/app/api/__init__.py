from app.api.forecast import router as forecast_router
from app.api.health import router as health_router

__all__ = ["health_router", "forecast_router"]
