"""Audio schemas."""

from enum import Enum

from pydantic import BaseModel, Field


class TestType(str, Enum):
    sustained_vowel = "sustained_vowel"
    vowel_sequence = "vowel_sequence"
    sentence_reading = "sentence_reading"


class RiskLevel(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class DiseaseCategory(str, Enum):
    movement_disorder = "Movement Disorder"
    neurodegenerative = "Neurodegenerative"
    motor_neuron = "Motor Neuron Disease"
    autoimmune = "Autoimmune Disorder"
    vascular = "Vascular"


class AudioUploadMeta(BaseModel):
    filename: str = Field(..., min_length=1)
    content_type: str = Field(default="audio/wav")
    test_type: TestType = Field(default=TestType.sustained_vowel)
