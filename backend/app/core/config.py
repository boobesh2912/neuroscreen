"""Application settings."""

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEFAULT_DEV_SECRET = "change-this-in-production"


def _resolve_relative_path(path_value: str, candidates: list[Path]) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    for base in candidates:
        candidate = base / path
        if candidate.exists():
            return candidate
    return candidates[0] / path


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5000
    PORT: int | None = None
    DEBUG: bool = False
    API_TITLE: str = "MediGuardian API"
    API_DESCRIPTION: str = "Multi-disease voice screening platform"
    API_VERSION: str = "1.0.0"

    SECRET_KEY: str = DEFAULT_DEV_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MODEL_PATH: str = "models/parkinson_model.pkl"
    FEATURE_NAMES_PATH: str = "models/feature_names.txt"
    DATABASE_URL: str | None = None
    DATABASE_PATH: str = "database/mediguardian.db"
    DATABASE_SSL_MODE: str = "require"
    DB_POOL_MIN_SIZE: int = 1
    DB_POOL_MAX_SIZE: int = 5
    DB_CONNECT_MAX_RETRIES: int = 8
    DB_CONNECT_RETRY_DELAY_SECONDS: float = 1.5
    ALLOW_SQLITE_IN_PRODUCTION: bool = False
    TEMP_DIR: str = "temp"
    UPLOAD_SUBDIR: str = "uploads"

    MAX_AUDIO_DURATION: int = 30
    MIN_AUDIO_DURATION: int = 3
    SUPPORTED_FORMATS: list[str] = ["wav", "mp3", "ogg", "flac", "m4a"]
    MAX_FILE_SIZE_MB: int = 50

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_ORIGIN_REGEX: str | None = r"http://(localhost|127\.0\.0\.1):\d+"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["Authorization", "Content-Type"]

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in raw.split(",") if item.strip()]
        return value

    @field_validator("SUPPORTED_FORMATS", mode="before")
    @classmethod
    def parse_formats(cls, value: Any) -> Any:
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item).strip().lower() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [item.strip().lower() for item in raw.split(",") if item.strip()]
        return value

    @field_validator("CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_csv_or_json_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in raw.split(",") if item.strip()]
        return value

    @field_validator("CORS_ALLOW_ORIGIN_REGEX", mode="before")
    @classmethod
    def parse_origin_regex(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @property
    def is_production(self) -> bool:
        env = self.ENVIRONMENT.lower()
        return env in {"prod", "production"} or os.getenv("RENDER", "").lower() == "true"

    @property
    def runtime_port(self) -> int:
        return int(self.PORT or self.API_PORT)

    @property
    def database_backend(self) -> str:
        if self.DATABASE_URL:
            normalized = self.DATABASE_URL.lower()
            if normalized.startswith("postgres://") or normalized.startswith("postgresql://") or normalized.startswith(
                "postgresql+psycopg://"
            ):
                return "postgresql"
            if normalized.startswith("sqlite:///"):
                return "sqlite"
            raise ValueError("Unsupported DATABASE_URL. Use postgresql://... or sqlite:///...")
        return "sqlite"

    @property
    def postgres_dsn(self) -> str:
        if self.database_backend != "postgresql" or not self.DATABASE_URL:
            raise ValueError("PostgreSQL DSN is only available when DATABASE_URL points to PostgreSQL.")

        dsn = self.DATABASE_URL
        if dsn.startswith("postgres://"):
            dsn = "postgresql://" + dsn[len("postgres://") :]
        if dsn.startswith("postgresql+psycopg://"):
            dsn = "postgresql://" + dsn[len("postgresql+psycopg://") :]

        parsed = urlparse(dsn)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if "sslmode" not in query and self.DATABASE_SSL_MODE:
            query["sslmode"] = self.DATABASE_SSL_MODE

        return urlunparse(parsed._replace(query=urlencode(query)))

    @property
    def model_full_path(self) -> Path:
        return _resolve_relative_path(self.MODEL_PATH, [BACKEND_ROOT, PROJECT_ROOT])

    @property
    def feature_names_full_path(self) -> Path:
        return _resolve_relative_path(self.FEATURE_NAMES_PATH, [BACKEND_ROOT, PROJECT_ROOT])

    @property
    def database_full_path(self) -> Path:
        if self.database_backend == "sqlite":
            if self.DATABASE_URL and self.DATABASE_URL.startswith("sqlite:///"):
                raw = self.DATABASE_URL.replace("sqlite:///", "", 1)
                path = Path(raw)
                if path.is_absolute():
                    return path
                return BACKEND_ROOT / raw
            return _resolve_relative_path(self.DATABASE_PATH, [BACKEND_ROOT, PROJECT_ROOT])

        raise ValueError("database_full_path is only available for SQLite backends.")

    @property
    def temp_full_path(self) -> Path:
        return BACKEND_ROOT / self.TEMP_DIR

    @property
    def upload_full_path(self) -> Path:
        return self.temp_full_path / self.UPLOAD_SUBDIR

    def validate_runtime(self) -> None:
        if self.CORS_ALLOW_CREDENTIALS and "*" in self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS cannot include '*' when CORS_ALLOW_CREDENTIALS is enabled.")

        if self.DB_POOL_MIN_SIZE < 1:
            raise ValueError("DB_POOL_MIN_SIZE must be >= 1.")
        if self.DB_POOL_MAX_SIZE < self.DB_POOL_MIN_SIZE:
            raise ValueError("DB_POOL_MAX_SIZE must be >= DB_POOL_MIN_SIZE.")
        if self.DB_CONNECT_MAX_RETRIES < 1:
            raise ValueError("DB_CONNECT_MAX_RETRIES must be >= 1.")
        if self.DB_CONNECT_RETRY_DELAY_SECONDS < 0:
            raise ValueError("DB_CONNECT_RETRY_DELAY_SECONDS must be >= 0.")

        insecure = {"", DEFAULT_DEV_SECRET, "mediguardian-secret-key-change-in-production"}
        if self.is_production:
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production.")
            if self.SECRET_KEY in insecure:
                raise ValueError("SECRET_KEY must be set to a strong production value.")
            if self.database_backend == "sqlite" and not self.ALLOW_SQLITE_IN_PRODUCTION:
                raise ValueError(
                    "SQLite is blocked in production by default. Configure a PostgreSQL DATABASE_URL or set "
                    "ALLOW_SQLITE_IN_PRODUCTION=True intentionally."
                )


settings = Settings()
