import platform
import subprocess
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.exceptions import register_exception_handlers
from backend.app.api.middleware import (
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
    TelemetryMiddleware,
)
from backend.app.api.routers import api_v1_router
from backend.app.config import settings
from backend.app.logging import logger


def _get_git_commit() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_time = time.perf_counter()
    commit_sha = _get_git_commit()
    py_version = platform.python_version()

    logger.info(
        "Initializing Repository Intelligence Platform backend",
        extra={
            "environment": settings.app.environment,
            "app_name": settings.app.app_name,
            "version": "1.0.0",
            "git_commit": commit_sha,
            "python_version": py_version,
            "model_version": "v1.0",
            "feature_schema_version": 1,
        },
    )

    startup_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info("Startup sequence completed successfully", extra={"startup_time_ms": startup_ms})

    yield

    logger.info("Caught SIGTERM / shutdown signal. Starting graceful shutdown sequence...")
    # Flush logs and close open resources
    logger.info("Graceful shutdown completed successfully. Exiting clean.")


app = FastAPI(
    title=settings.app.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register Exception Handlers
register_exception_handlers(app)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Structured Logging & Telemetry middleware
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TelemetryMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
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
