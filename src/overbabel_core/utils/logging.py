"""Structured logging bootstrap using structlog."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

import structlog


def setup_logging() -> None:
    """Configure structlog once per process (idempotent enough for Phase 1)."""
    level_name = os.environ.get("OVERBABEL_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Return a structlog logger for the given dotted name."""
    return structlog.get_logger(name)
