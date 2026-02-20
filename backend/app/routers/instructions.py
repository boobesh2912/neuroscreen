"""Recording instruction routes."""

import logging

from fastapi import APIRouter, HTTPException

from app.services.disease_analyzer import DiseaseAnalyzer


router = APIRouter()
_disease_analyzer = DiseaseAnalyzer()
logger = logging.getLogger("mediguardian.instructions")


@router.get("/recording-instructions/{test_type}")
async def recording_instructions(test_type: str):
    try:
        return {"success": True, "instructions": _disease_analyzer.recording_instructions(test_type)}
    except Exception as exc:
        logger.exception("Failed to load recording instructions for test_type=%s", test_type)
        raise HTTPException(status_code=500, detail="Failed to load recording instructions") from exc
