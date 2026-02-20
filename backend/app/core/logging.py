"""Application logging configuration."""

from __future__ import annotations

from logging.config import dictConfig


_CONFIGURED = False


def configure_logging(log_level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = (log_level or "INFO").upper()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": level,
            },
            "loggers": {
                "uvicorn.error": {"level": level},
                "uvicorn.access": {"level": level},
                "httpx": {"level": "WARNING"},
                "mediguardian": {"level": level, "handlers": ["default"], "propagate": False},
            },
        }
    )
    _CONFIGURED = True
