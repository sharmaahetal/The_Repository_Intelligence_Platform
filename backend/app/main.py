from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import forecast_router, health_router
from app.config import settings
from app.logging import TelemetryMiddleware, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Repository Intelligence Platform backend...")
    yield
    logger.info("Shutting down Repository Intelligence Platform backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Telemetry middleware
app.add_middleware(TelemetryMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(forecast_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Repository Intelligence Platform (RIP) API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
