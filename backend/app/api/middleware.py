import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.logging import bind_contextvars, logger


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware attaching request_id and binding request parameters into log context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Extract repo path param or query param if present
        repo = request.query_params.get("repo") or request.query_params.get("repository") or "unknown"
        bind_contextvars(repository=repo)

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        return response
