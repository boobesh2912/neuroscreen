"""Validation utilities."""

from pathlib import Path

from app.core.config import settings


def validate_extension(filename: str) -> str:
    if "." not in filename:
        raise ValueError("File must include an extension")
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in settings.SUPPORTED_FORMATS:
        raise ValueError(f"Invalid file type. Allowed: {', '.join(settings.SUPPORTED_FORMATS)}")
    return ext


def ensure_path_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(str(path))
