from contextlib import asynccontextmanager

from app.config import settings
from app.logging import TelemetryMiddleware, logger
from backend.app.api.exceptions import register_exception_handlers
from backend.app.api.middleware import StructuredLoggingMiddleware
from backend.app.api.routers import api_v1_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Repository Intelligence Platform backend...")
    yield
    logger.info("Shutting down Repository Intelligence Platform backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register Exception Handlers
register_exception_handlers(app)

# Structured Logging & Telemetry middleware
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TelemetryMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Repository Intelligence Platform (RIP) API",
        "docs": "/docs",
        "health": "/api/v1/health/live",
    }
