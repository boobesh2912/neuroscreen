"""API response schemas."""

from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.audio import TestType
from app.schemas.disease import BiomarkerResult, DiseaseProbability, ModelSignals, PrimaryDiagnosis


class Visualizations(BaseModel):
    waveform_url: str
    spectrogram_url: str


class KeyFeatures(BaseModel):
    f0_mean: float
    jitter_relative: float
    shimmer_relative: float
    hnr: float
    f0_tremor_intensity: float
    voice_breaks: float
    formant_f1: float
    formant_f2: float


NonEmptyStr = Annotated[str, Field(min_length=1)]


class MultiDiseaseAnalysisResponse(BaseModel):
    success: bool
    test_type: TestType
    primary_diagnosis: PrimaryDiagnosis
    all_diseases: list[DiseaseProbability]
    overall_risk_score: int = Field(ge=0, le=100)
    key_features: KeyFeatures
    biomarkers: list[BiomarkerResult]
    recommendations: list[NonEmptyStr] = Field(min_length=1)
    specialist_needed: list[str] | None = None
    visualizations: Visualizations
    audio_file: str
    model_signals: ModelSignals
