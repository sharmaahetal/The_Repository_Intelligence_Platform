import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.logging.context import clear_request_context, set_request_context
from backend.app.logging.logger import logger


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware binding request-scoped correlation IDs to contextvars and logging request latency."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = (
            request.headers.get("X-Request-ID")
            or request.headers.get("X-Correlation-ID")
            or str(uuid.uuid4())[:8]
        )
        request.state.request_id = request_id
        user_agent = request.headers.get("user-agent", "unknown")

        set_request_context(
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            user_agent=user_agent,
        )

        start_time = time.perf_counter()
        try:
            response: Response = await call_next(request)
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-MS"] = f"{process_time_ms:.2f}"

            log_level = logger.error if response.status_code >= 400 else logger.info
            log_level(
                f"HTTP {request.method} {request.url.path} -> Status={response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "latency_ms": process_time_ms,
                },
            )
            return response
        finally:
            clear_request_context()
