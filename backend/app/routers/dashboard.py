"""Dashboard routes."""

import ast
import json

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.services.booking_service import booking_service


router = APIRouter()


@router.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    tests = booking_service.get_user_tests(current_user["user_id"])

    test_history = []
    for test in tests:
        confidence = float(test["confidence"])
        prediction = test["prediction"]
        risk_score = int(confidence * 100) if prediction == "parkinsons" else int((1 - confidence) * 100)
        test_history.append(
            {
                "id": test["id"],
                "date": test["test_date"],
                "prediction": prediction,
                "confidence": confidence,
                "risk_score": risk_score,
                "test_type": test["test_type"],
            }
        )

    total_tests = len(test_history)
    avg_confidence = sum(t["confidence"] for t in test_history) / total_tests if total_tests else 0
    latest_risk = test_history[0]["risk_score"] if test_history else 0

    return {
        "success": True,
        "user": current_user,
        "statistics": {
            "total_tests": total_tests,
            "avg_confidence": round(avg_confidence * 100, 1),
            "latest_risk_score": latest_risk,
        },
        "test_history": test_history,
    }


@router.get("/results/{test_id}")
async def get_result(test_id: str, current_user: dict = Depends(get_current_user)):
    tests = booking_service.get_user_tests(current_user["user_id"])
    selected = next((item for item in tests if item["id"] == test_id), None)
    if selected is None:
        raise HTTPException(status_code=404, detail="Test not found")

    try:
        features = json.loads(selected["features"])
    except Exception:
        try:
            features = ast.literal_eval(selected["features"])
        except Exception:
            features = {}

    return {
        "success": True,
        "test": {
            "id": selected["id"],
            "date": selected["test_date"],
            "prediction": selected["prediction"],
            "confidence": float(selected["confidence"]),
            "features": features,
            "audio_file": selected.get("audio_file_path"),
        },
    }
