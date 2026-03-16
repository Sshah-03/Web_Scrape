"""Logging configuration helpers."""

from logging.config import dictConfig

from app.config import settings


def setup_logging() -> None:
    """Configure structured application logging."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": settings.LOG_LEVEL,
                }
            },
            "root": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        }
    )
