"""FastAPI lifespan state management."""

from contextlib import asynccontextmanager
import logging
from typing import Any
from urllib.parse import urlparse, urlunparse

from fastapi import FastAPI
import joblib

from app.core.config import settings
from app.core.database import close_database, init_database

_model: Any = None
_feature_names: list[str] = []
logger = logging.getLogger("mediguardian.startup")


def get_model() -> Any:
    return _model


def get_parkinson_model() -> Any:
    return _model


def get_feature_names() -> list[str]:
    return _feature_names


def _safe_database_target() -> str:
    if settings.database_backend == "sqlite":
        return str(settings.database_full_path)

    parsed = urlparse(settings.postgres_dsn)
    masked_netloc = parsed.netloc
    if "@" in parsed.netloc:
        credentials, host = parsed.netloc.split("@", 1)
        user = credentials.split(":", 1)[0]
        masked_netloc = f"{user}:***@{host}"
    return urlunparse(parsed._replace(netloc=masked_netloc))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _feature_names

    settings.validate_runtime()
    settings.temp_full_path.mkdir(parents=True, exist_ok=True)
    settings.upload_full_path.mkdir(parents=True, exist_ok=True)
    init_database()

    if settings.model_full_path.exists():
        try:
            _model = joblib.load(settings.model_full_path)
        except Exception as exc:
            logger.exception("Failed to load Parkinson model from %s: %s", settings.model_full_path, exc)
            _model = None
    else:
        logger.warning("Parkinson model file not found: %s", settings.model_full_path)
        _model = None

    if settings.feature_names_full_path.exists():
        try:
            _feature_names = settings.feature_names_full_path.read_text(encoding="utf-8").splitlines()
        except Exception as exc:
            logger.exception("Failed to load feature names from %s: %s", settings.feature_names_full_path, exc)
            _feature_names = []
    else:
        logger.warning("Feature names file not found: %s", settings.feature_names_full_path)
        _feature_names = []

    logger.info(
        "Startup completed: model_loaded=%s feature_count=%s db_backend=%s db_target=%s",
        _model is not None,
        len(_feature_names),
        settings.database_backend,
        _safe_database_target(),
    )
    yield

    close_database()
    _model = None
    _feature_names = []
