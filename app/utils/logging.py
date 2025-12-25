"""Logging configuration for structured logging and error tracking."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from app.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request ID if available
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Add user ID if available
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        # Add extra fields
        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add stack info if present
        if record.stack_info:
            log_entry["stack_info"] = record.stack_info

        return json.dumps(log_entry, ensure_ascii=False)


class HumanFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human reading."""
        # Base format
        formatted = super().format(record)

        # Add request ID if available
        if hasattr(record, "request_id"):
            formatted = f"[{record.request_id}] {formatted}"

        # Add user ID if available
        if hasattr(record, "user_id"):
            formatted = f"[user:{record.user_id}] {formatted}"

        return formatted


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Determine log level
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Choose formatter based on environment
    formatter: logging.Formatter
    if settings.debug:
        formatter = HumanFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = JSONFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    configure_loggers(log_level)


def configure_loggers(log_level: int) -> None:
    """Configure specific logger levels."""
    # Application loggers
    logging.getLogger("app").setLevel(log_level)

    # Third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding context to log records."""

    def __init__(self, **context: Any):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()

    def __enter__(self) -> "LogContext":
        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        logging.setLogRecordFactory(self.old_factory)


def log_with_context(
    logger: logging.Logger, level: int, message: str, **context: Any
) -> None:
    """Log a message with additional context."""
    with LogContext(**context):
        logger.log(level, message)
