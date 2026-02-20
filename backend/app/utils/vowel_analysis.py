"""Compatibility wrappers for voice feature extraction."""

from typing import Any

from app.ml.vowel_analysis import analyze_vowel_sequence, extract_vowel_features


def extract_features_by_test_type(y: Any, sr: int, test_type: str) -> dict:
    if test_type == "vowel_sequence":
        return analyze_vowel_sequence(y, sr)
    return extract_vowel_features(y, sr, vowel_type="sustained")
