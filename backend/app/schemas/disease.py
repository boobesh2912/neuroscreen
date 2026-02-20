"""Disease result schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.audio import RiskLevel


class DiseaseProbability(BaseModel):
    disease: str
    disease_name: str
    probability: float = Field(..., ge=0, le=100)
    category: Optional[str] = None


class PrimaryDiagnosis(BaseModel):
    disease: str
    disease_name: str
    probability: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    category: Optional[str] = None


class BiomarkerResult(BaseModel):
    name: str
    value: float
    unit: str
    normal_range: str
    clinical_significance: str


class ModelSignals(BaseModel):
    rule_based_used: bool
    multi_disease_model_used: bool
    parkinson_model_used: bool
    parkinson_model_probability: Optional[float] = Field(default=None, ge=0, le=100)
