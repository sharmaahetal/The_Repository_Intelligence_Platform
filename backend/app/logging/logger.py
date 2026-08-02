import functools
import logging
import os
import sys
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

from backend.app.logging.context import get_request_context
from backend.app.logging.formatter import ConsoleFormatter, JSONFormatter

F = TypeVar("F", bound=Callable[..., Any])


class ContextInjectingFilter(logging.Filter):
    """Logging filter that automatically injects active request_id and contextvars into all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = get_request_context()
        for k, v in ctx.items():
            if not hasattr(record, k):
                setattr(record, k, v)
        return True


def setup_logger(name: str = "rip_backend") -> logging.Logger:
    """Configures application logger with context injection, secret redaction, and environment-aware formatters."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Attach context injection filter
    if not any(isinstance(f, ContextInjectingFilter) for f in logger.filters):
        logger.addFilter(ContextInjectingFilter())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        
        env_val = os.getenv("ENVIRONMENT", "development").lower()
        is_prod = (
            env_val in ("production", "prod")
            or os.getenv("LOG_FORMAT", "").lower() == "json"
        )

        if is_prod:
            formatter = JSONFormatter(
                service_name="rip_backend",
                version="1.0.0",
                environment=env_val,
            )
        else:
            formatter = ConsoleFormatter(
                fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()


@contextmanager
def log_duration(event_name: str, level: int = logging.INFO, **extra: Any):
    """Context manager measuring execution latency of code blocks and logging duration."""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.log(
            level,
            f"Event [{event_name}] completed in {latency_ms}ms",
            extra={"event_name": event_name, "latency_ms": latency_ms, **extra},
        )


def log_execution_time(event_name: str | None = None, level: int = logging.INFO) -> Callable[[F], F]:
    """Decorator measuring function execution time and logging latency."""

    def decorator(func: F) -> F:
        evt = event_name or func.__qualname__

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with log_duration(evt, level=level):
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.log(
                    level,
                    f"Event [{evt}] completed in {latency_ms}ms",
                    extra={"event_name": evt, "latency_ms": latency_ms},
                )

        if asyncio_is_coroutine_function(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def asyncio_is_coroutine_function(func: Any) -> bool:
    import inspect
    return inspect.iscoroutinefunction(func)
