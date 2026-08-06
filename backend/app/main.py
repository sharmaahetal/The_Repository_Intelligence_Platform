"""Main FastAPI application entry point for Repository Intelligence Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.exceptions import register_exception_handlers
from backend.app.api.middleware import (
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
    TelemetryMiddleware,
)
from backend.app.api.router import router as api_router
from backend.app.api.routers import api_v1_router
from backend.app.config import settings

app = FastAPI(
    title=settings.app.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception Handlers & Security Middlewares
register_exception_handlers(app)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TelemetryMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include root API router and v1 router
app.include_router(api_router)
app.include_router(api_v1_router)


@app.get("/health")
async def health_check():
    """Simple health check endpoint returning application status."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint welcoming API clients."""
    return {
        "message": "Welcome to Repository Intelligence Platform (RIP) API",
        "docs": "/docs",
        "health": "/health",
    }
