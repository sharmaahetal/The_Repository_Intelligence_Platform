from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

_REQUEST_CONTEXT: ContextVar[dict[str, Any]] = ContextVar("request_context", default={})


def set_request_context(request_id: str, **kwargs: Any) -> dict[str, Any]:
    """Sets or replaces current request-scoped context dictionary."""
    ctx = {"request_id": request_id, **kwargs}
    _REQUEST_CONTEXT.set(ctx)
    return ctx


def get_request_context() -> dict[str, Any]:
    """Returns a copy of current request-scoped context dictionary."""
    return dict(_REQUEST_CONTEXT.get({}))


def clear_request_context() -> None:
    """Clears current request-scoped context dictionary."""
    _REQUEST_CONTEXT.set({})


def bind_contextvars(**kwargs: Any) -> dict[str, Any]:
    """Binds additional key-value pairs into active request context."""
    current = get_request_context()
    current.update(kwargs)
    _REQUEST_CONTEXT.set(current)
    return current


def unbind_contextvars(*keys: str) -> dict[str, Any]:
    """Removes specified keys from active request context."""
    current = get_request_context()
    for key in keys:
        current.pop(key, None)
    _REQUEST_CONTEXT.set(current)
    return current


@contextmanager
def log_context(request_id: str | None = None, **kwargs: Any):
    """Context manager for binding request context variables temporarily."""
    current = get_request_context()
    new_ctx = dict(current)
    if request_id:
        new_ctx["request_id"] = request_id
    new_ctx.update(kwargs)

    token = _REQUEST_CONTEXT.set(new_ctx)
    try:
        yield new_ctx
    finally:
        _REQUEST_CONTEXT.reset(token)
