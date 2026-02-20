"""Static file serving routes for generated artifacts."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.security import get_current_user


router = APIRouter()


def _safe_filename(filename: str) -> str:
    safe = Path(filename).name
    if safe != filename:
        raise HTTPException(status_code=404, detail="File not found")
    return safe


@router.get("/temp/{filename}")
async def serve_temp_file(filename: str):
    target = settings.temp_full_path / _safe_filename(filename)
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)


@router.get("/uploads/{filename}")
async def serve_upload_file(filename: str, current_user: dict = Depends(get_current_user)):
    target = settings.upload_full_path / _safe_filename(filename)
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)
