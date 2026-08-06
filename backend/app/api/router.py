"""Root API router combining feature routers for Repository Intelligence Platform."""

from fastapi import APIRouter

from backend.app.api.explanations import router as explanations_router
from backend.app.api.model_versions import router as model_versions_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.repositories import router as repositories_router
from backend.app.api.snapshots import router as snapshots_router

router = APIRouter()

router.include_router(repositories_router)
router.include_router(snapshots_router)
router.include_router(predictions_router)
router.include_router(explanations_router)
router.include_router(model_versions_router)
