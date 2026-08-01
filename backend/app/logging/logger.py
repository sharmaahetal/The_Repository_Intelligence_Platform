import logging
import sys

STANDARD_LOG_FIELDS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName", "processName",
    "process", "asctime", "message"
}


class StructuredFormatter(logging.Formatter):
    """Logging formatter that appends extra context attributes cleanly."""

    def format(self, record: logging.LogRecord) -> str:
        base_message = super().format(record)
        extra_items = {
            k: v for k, v in record.__dict__.items() if k not in STANDARD_LOG_FIELDS
        }
        if extra_items:
            extra_str = " ".join(f"{k}={v}" for k, v in extra_items.items())
            return f"{base_message} | {extra_str}"
        return base_message


def setup_logger(name: str = "rip_backend") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = StructuredFormatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()

