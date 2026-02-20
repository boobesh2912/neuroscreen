"""Disease analysis service."""

from pathlib import Path

from app.ml.multi_disease_detector import analyze_multi_disease, get_recording_instructions

from app.schemas.audio import TestType
from app.schemas.response import MultiDiseaseAnalysisResponse


class DiseaseAnalyzer:
    def analyze(self, audio_path: Path, test_type: TestType, visualizations: dict) -> MultiDiseaseAnalysisResponse:
        result = analyze_multi_disease(str(audio_path), test_type=test_type.value)
        result["test_type"] = test_type.value
        result["visualizations"] = visualizations
        result["audio_file"] = audio_path.name
        return MultiDiseaseAnalysisResponse.model_validate(result)

    def recording_instructions(self, test_type: str) -> dict:
        return get_recording_instructions(test_type)
