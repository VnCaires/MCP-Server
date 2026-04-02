from __future__ import annotations

import json
import logging
import sys
from typing import Any


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "context"):
            payload["context"] = record.context
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("project.server")
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    message: str,
    **context: Any,
) -> None:
    logger.log(level, message, extra={"event": event, "context": context})
