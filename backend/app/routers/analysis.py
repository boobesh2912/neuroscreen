"""Voice analysis routes."""

from datetime import datetime
import logging

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
import numpy as np
import pandas as pd

from app.core.lifespan import get_feature_names, get_model
from app.core.security import decode_access_token
from app.schemas.audio import TestType
from app.schemas.response import MultiDiseaseAnalysisResponse
from app.ml.advanced_features import extract_advanced_features
from app.ml.vowel_analysis import classify_disease_from_features
from app.services.audio_processor import AudioProcessor
from app.services.booking_service import booking_service
from app.services.disease_analyzer import DiseaseAnalyzer


router = APIRouter()
audio_processor = AudioProcessor()
disease_analyzer = DiseaseAnalyzer()
logger = logging.getLogger("mediguardian.analysis")


@router.post("", summary="Analyze uploaded audio for Parkinson's")
async def analyze_audio(
    audio: UploadFile | None = File(default=None, description="Audio file"),
    authorization: str | None = Header(default=None),
):
    try:
        if audio is None:
            raise HTTPException(status_code=400, detail="No audio file provided")

        audio_path = await audio_processor.save_upload(audio)
        y, sr, clinical_features = audio_processor.extract_features(audio_path, TestType.sustained_vowel)
        features = extract_advanced_features(y, sr)
        disease_indicators = classify_disease_from_features(clinical_features)

        model = get_model()
        feature_names = get_feature_names()
        if model is None:
            raise HTTPException(status_code=503, detail="Prediction model is not available on server")

        if feature_names:
            feature_values = [features.get(name, 0) for name in feature_names]
            feature_array = np.array([feature_values])
        else:
            features_df = pd.DataFrame([features])
            for col in ["filename", "label"]:
                if col in features_df.columns:
                    features_df = features_df.drop(col, axis=1)
            feature_array = features_df.values

        probability = model.predict_proba(feature_array)[0]
        parkinsons_prob = float(probability[1] if len(probability) > 1 else 0.5)
        prediction = "parkinsons" if parkinsons_prob > 0.7 else "healthy"
        confidence = parkinsons_prob if prediction == "parkinsons" else (1 - parkinsons_prob)
        risk_score = int(parkinsons_prob * 100)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        visualizations = audio_processor.generate_visualizations(y, sr, timestamp)

        if authorization and authorization.lower().startswith("bearer "):
            payload = decode_access_token(authorization.split(" ", 1)[1])
            if payload:
                booking_service.save_test_result(
                    user_id=payload["user_id"],
                    test_type="parkinsons_voice",
                    prediction=prediction,
                    confidence=confidence,
                    features=features,
                    audio_path=str(audio_path),
                )

        recommendations = (
            [
                "Your voice patterns show normal characteristics",
                "Continue monitoring with regular tests",
                "Maintain a healthy lifestyle and stay active",
            ]
            if prediction == "healthy"
            else [
                "Consult with a healthcare professional for comprehensive evaluation",
                "Consider scheduling a neurological examination",
                "Keep track of any physical symptoms (tremors, stiffness, balance issues)",
            ]
        )

        return {
            "success": True,
            "prediction": prediction,
            "confidence": float(confidence),
            "risk_score": risk_score,
            "parkinsons_score": round(parkinsons_prob * 100, 2),
            "features": {
                "jitter_relative": float(features.get("jitter_relative", 0)),
                "shimmer_relative": float(features.get("shimmer_relative", 0)),
                "hnr": float(features.get("hnr", 0)),
                "f0_mean": float(features.get("f0_mean", 0)),
            },
            "disease_indicators": {
                key: round(float(value), 2) for key, value in disease_indicators.items()
            },
            "visualizations": visualizations,
            "recommendations": recommendations,
            "audio_file": audio_path.name,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/multi-disease", response_model=MultiDiseaseAnalysisResponse)
async def analyze_multi_disease(
    audio: UploadFile | None = File(default=None, description="Audio file (WAV/MP3/OGG/FLAC/M4A)"),
    test_type: TestType = Form(TestType.sustained_vowel),
    authorization: str | None = Header(default=None),
):
    try:
        if audio is None:
            raise HTTPException(status_code=400, detail="No audio file provided")

        audio_path = await audio_processor.save_upload(audio)
        y, sr, _ = audio_processor.extract_features(audio_path, test_type)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        visualizations = audio_processor.generate_visualizations(y, sr, timestamp)

        result = disease_analyzer.analyze(audio_path, test_type, visualizations)

        if authorization and authorization.lower().startswith("bearer "):
            payload = decode_access_token(authorization.split(" ", 1)[1])
            if payload:
                primary = result.primary_diagnosis
                booking_service.save_test_result(
                    user_id=payload["user_id"],
                    test_type=f"multi_disease_{test_type.value}",
                    prediction=primary.disease,
                    confidence=primary.probability / 100.0,
                    features=result.key_features.model_dump(),
                    audio_path=str(audio_path),
                )

        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Multi-disease analysis failed")
        raise HTTPException(status_code=500, detail="Analysis failed due to an internal server error") from exc
