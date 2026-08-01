import time
import uuid
from typing import Callable

from app.logging import logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware attaching request_id and logging request method, path, repository, latency, and status code."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Extract repo path param if present
        repo = request.path_params.get("repo", "unknown") if hasattr(request, "path_params") else "unknown"

        logger.info(
            f"API Request [{request.method} {request.url.path}] -> {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "repository": repo,
            },
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        return response
