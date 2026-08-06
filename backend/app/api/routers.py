from fastapi import APIRouter

from backend.app.api.forecast import router as forecast_router
from backend.app.api.health import router as health_router
from backend.app.api.metrics_router import router as metrics_router
from backend.app.api.router import api_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(forecast_router)
api_v1_router.include_router(metrics_router)
api_v1_router.include_router(api_router)
