from fastapi import APIRouter

from backend.app.api.forecast import router as forecast_router
from backend.app.api.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(forecast_router)
