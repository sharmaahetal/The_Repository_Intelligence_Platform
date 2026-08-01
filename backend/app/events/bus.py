import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from backend.app.events.types import Event
from backend.app.logging import logger

E = TypeVar("E", bound=Event)
EventHandler = Callable[[Any], Awaitable[None]] | Callable[[Any], None]


class EventBus:
    """In-process asynchronous event dispatcher executing decoupled domain event handlers."""

    def __init__(self) -> None:
        self._subscribers: dict[type[Event], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[E], handler: EventHandler) -> None:
        """Subscribes an event handler callback to a specific event type."""
        self._subscribers[event_type].append(handler)
        logger.info(
            "Subscribed handler to event",
            extra={"event_type": event_type.__name__, "handler": handler.__name__},
        )

    async def publish(self, event: Event) -> None:
        """Publishes an event instance to all registered handlers asynchronously."""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        if not handlers:
            logger.debug("No handlers registered for event", extra={"event_type": event_type.__name__})
            return

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as exc:
                logger.error(
                    "Error executing event handler",
                    extra={"event_type": event_type.__name__, "handler": handler.__name__, "error": str(exc)},
                )


# Global singleton event bus instance
default_event_bus = EventBus()
