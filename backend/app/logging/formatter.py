import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

SENSITIVE_KEYS = {
    "token",
    "github_token",
    "secret",
    "password",
    "authorization",
    "cookie",
    "set-cookie",
    "api_key",
    "access_token",
    "refresh_token",
    "database_url",
    "redis_url",
    "db_url",
    "cred",
    "credentials",
}

URL_CREDENTIALS_REGEX = re.compile(
    r"(postgres|postgresql|mysql|redis|mongodb)(\+[a-z0-9]+)?://([^:]+):([^@]+)@",
    re.IGNORECASE,
)
BEARER_AUTH_REGEX = re.compile(
    r"(Bearer|Token|Basic)\s+[A-Za-z0-9._~\-+/=]+",
    re.IGNORECASE,
)
GITHUB_PAT_REGEX = re.compile(
    r"ghp_[A-Za-z0-9_]{36,255}|github_pat_[A-Za-z0-9_]{22,255}",
    re.IGNORECASE,
)


def redact_sensitive_string(text: str) -> str:
    """Redacts passwords, tokens, auth headers, and connection string credentials in text strings."""
    if not text:
        return text
    text = URL_CREDENTIALS_REGEX.sub(r"\1\2://[REDACTED]@", text)
    text = BEARER_AUTH_REGEX.sub(r"\1 [REDACTED]", text)
    text = GITHUB_PAT_REGEX.sub("[REDACTED_GITHUB_TOKEN]", text)
    return text


def redact_sensitive_data(val: Any) -> Any:
    """Recursively redacts sensitive values from dictionaries, lists, strings, and headers."""
    if isinstance(val, str):
        return redact_sensitive_string(val)

    if isinstance(val, dict):
        redacted = {}
        for k, v in val.items():
            k_lower = str(k).lower()
            if any(s_key in k_lower for s_key in SENSITIVE_KEYS):
                redacted[k] = "[REDACTED]"
            else:
                redacted[k] = redact_sensitive_data(v)
        return redacted

    if isinstance(val, list | tuple):
        return [redact_sensitive_data(item) for item in val]

    return val


STANDARD_LOG_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "asctime",
    "message",
}


class JSONFormatter(logging.Formatter):
    """Produces structured single-line JSON log output for ingestion by centralized log systems."""

    def __init__(self, service_name: str = "rip_backend", version: str = "1.0.0", environment: str = "development") -> None:
        super().__init__()
        self.service_name = service_name
        self.version = version
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service_name,
            "version": self.version,
            "environment": self.environment,
            "message": redact_sensitive_string(record.getMessage()),
        }

        # Inject extra context fields
        extra_fields = {
            k: redact_sensitive_data(v)
            for k, v in record.__dict__.items()
            if k not in STANDARD_LOG_FIELDS
        }
        log_obj.update(extra_fields)

        # Handle exception context
        if record.exc_info:
            exc_type, exc_val, _ = record.exc_info
            log_obj["exception"] = {
                "type": exc_type.__name__ if exc_type else "Exception",
                "message": redact_sensitive_string(str(exc_val)),
                "stacktrace": redact_sensitive_string(self.formatException(record.exc_info)),
            }

        return json.dumps(log_obj, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console log formatter for local development with context & redaction."""

    def format(self, record: logging.LogRecord) -> str:
        base_message = redact_sensitive_string(super().format(record))
        extra_items = {
            k: redact_sensitive_data(v)
            for k, v in record.__dict__.items()
            if k not in STANDARD_LOG_FIELDS
        }

        req_id = extra_items.pop("request_id", None)
        prefix = f" [req_id={req_id}]" if req_id else ""

        if extra_items:
            extra_str = " ".join(f"{k}={v}" for k, v in extra_items.items())
            return f"{base_message}{prefix} | {extra_str}"
        return f"{base_message}{prefix}"
