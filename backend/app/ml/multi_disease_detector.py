"""
Multi-Disease Voice Analysis System
Detects multiple neurological disorders from voice recordings

Supported Diseases:
1. Parkinson's Disease - Tremor, rigidity, reduced voice amplitude
2. Alzheimer's Disease - Hesitations, pauses, word-finding difficulties
3. ALS (Amyotrophic Lateral Sclerosis) - Progressive muscle weakness
4. Multiple Sclerosis - Coordination issues, scanning speech
5. Stroke/Aphasia - Speech impediments, articulation problems
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import librosa
import joblib
import numpy as np
import pandas as pd
from app.core.config import settings
from app.ml.advanced_features import extract_advanced_features
from app.ml.vowel_analysis import (
    analyze_vowel_sequence,
    classify_disease_from_features,
    extract_vowel_features,
)

# Disease configuration
DISEASE_PROFILES = {
    'parkinsons': {
        'name': 'Parkinson\'s Disease',
        'category': 'Movement Disorder',
        'key_biomarkers': ['f0_tremor_intensity', 'jitter_relative', 'shimmer_relative', 'hnr'],
        'specialists': ['Movement Disorders Specialist', 'Parkinson\'s Disease Specialist'],
        'description': 'Progressive neurological disorder affecting movement and voice control'
    },
    'alzheimers': {
        'name': 'Alzheimer\'s Disease',
        'category': 'Neurodegenerative',
        'key_biomarkers': ['num_voice_breaks', 'max_pause_duration', 'energy_entropy'],
        'specialists': ['Cognitive Neurologist', 'Geriatric Neurologist'],
        'description': 'Progressive memory loss and cognitive decline affecting speech patterns'
    },
    'als': {
        'name': 'ALS (Amyotrophic Lateral Sclerosis)',
        'category': 'Motor Neuron Disease',
        'key_biomarkers': ['rms_energy_mean', 'shimmer_relative', 'spectral_flux'],
        'specialists': ['Neuromuscular Specialist', 'ALS Specialist'],
        'description': 'Progressive muscle weakness including speech muscles (bulbar symptoms)'
    },
    'multiple_sclerosis': {
        'name': 'Multiple Sclerosis',
        'category': 'Autoimmune Disorder',
        'key_biomarkers': ['formant_transition_smoothness', 'f0_transition_smoothness'],
        'specialists': ['Multiple Sclerosis Specialist', 'General Neurologist'],
        'description': 'Immune system attacks nerve sheaths, affecting coordination and speech'
    },
    'stroke': {
        'name': 'Stroke/Aphasia',
        'category': 'Vascular',
        'key_biomarkers': ['formant_dispersion', 'zcr_mean'],
        'specialists': ['Stroke Specialist', 'Speech Neurologist'],
        'description': 'Interrupted blood flow to brain causing speech and articulation problems'
    }
}


Number = Union[int, float]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR_CANDIDATES = [
    settings.model_full_path.parent,
    PROJECT_ROOT / "models",
]


def _resolve_model_path(filename: str) -> Path:
    for directory in MODELS_DIR_CANDIDATES:
        candidate = directory / filename
        if candidate.exists():
            return candidate
    return MODELS_DIR_CANDIDATES[0] / filename

_MULTI_MODEL_DATA: Optional[Dict[str, Any]] = None
_PARKINSON_MODEL: Optional[Any] = None
_PARKINSON_FEATURES: List[str] = []


def _load_model_assets() -> None:
    """Load trained model assets from models/ lazily."""
    global _MULTI_MODEL_DATA, _PARKINSON_MODEL, _PARKINSON_FEATURES

    if _MULTI_MODEL_DATA is None:
        multi_path = _resolve_model_path("multi_disease_model_optimized.pkl")
        if multi_path.exists():
            try:
                model_data = joblib.load(str(multi_path))
                if isinstance(model_data, dict) and 'model' in model_data:
                    _MULTI_MODEL_DATA = model_data
            except Exception:
                _MULTI_MODEL_DATA = None

    if _PARKINSON_MODEL is None:
        park_path = _resolve_model_path("parkinson_model.pkl")
        if park_path.exists():
            try:
                _PARKINSON_MODEL = joblib.load(str(park_path))
            except Exception:
                _PARKINSON_MODEL = None

    if not _PARKINSON_FEATURES:
        feat_path = _resolve_model_path("feature_names.txt")
        if feat_path.exists():
            try:
                with feat_path.open("r", encoding="utf-8") as f:
                    _PARKINSON_FEATURES = [line.strip() for line in f.readlines() if line.strip()]
            except Exception:
                _PARKINSON_FEATURES = []


def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    total = float(sum(max(0.0, v) for v in scores.values()))
    if total <= 0:
        return scores
    return {k: (max(0.0, float(v)) / total) * 100.0 for k, v in scores.items()}


def _predict_multi_model_scores(features: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """Predict multi-disease probabilities using trained ensemble artifact."""
    if _MULTI_MODEL_DATA is None:
        return None
    try:
        feature_names = list(_MULTI_MODEL_DATA.get('feature_names', []))
        model = _MULTI_MODEL_DATA.get('model')
        scaler = _MULTI_MODEL_DATA.get('scaler')
        classes = [str(c) for c in _MULTI_MODEL_DATA.get('classes', [])]
        if not feature_names or model is None or scaler is None or not classes:
            return None

        row = [float(features.get(name, 0.0)) for name in feature_names]
        X = np.array([row], dtype=float)
        X_scaled = scaler.transform(X)
        probs = model.predict_proba(X_scaled)[0]
        return {cls: float(prob) * 100.0 for cls, prob in zip(classes, probs)}
    except Exception:
        return None


def _predict_parkinson_probability(advanced_features: Dict[str, Any]) -> Optional[float]:
    """Predict Parkinson probability from dedicated Parkinson model."""
    if _PARKINSON_MODEL is None:
        return None
    try:
        if _PARKINSON_FEATURES:
            row = [float(advanced_features.get(name, 0.0)) for name in _PARKINSON_FEATURES]
            X = np.array([row], dtype=float)
        else:
            X = pd.DataFrame([advanced_features]).astype(float).fillna(0.0)

        probs = _PARKINSON_MODEL.predict_proba(X)[0]

        classes = None
        if hasattr(_PARKINSON_MODEL, 'classes_'):
            classes = [str(c).lower() for c in _PARKINSON_MODEL.classes_]
        elif hasattr(_PARKINSON_MODEL, 'named_steps'):
            clf = _PARKINSON_MODEL.named_steps.get('classifier')
            if clf is not None and hasattr(clf, 'classes_'):
                classes = [str(c).lower() for c in clf.classes_]

        if classes:
            if 'parkinsons' in classes:
                return float(probs[classes.index('parkinsons')]) * 100.0
            if '1' in classes:
                return float(probs[classes.index('1')]) * 100.0

        return float(probs[-1]) * 100.0
    except Exception:
        return None


def _apply_parkinson_boost(scores: Dict[str, float], features: Dict[str, Any], park_prob: Optional[float]) -> Dict[str, float]:
    """Boost Parkinson score for severe biomarker patterns."""
    jitter = float(_feature_value(features, 'jitter_relative', 0))
    shimmer = float(_feature_value(features, 'shimmer_relative', 0))
    hnr = float(_feature_value(features, 'hnr', 20))
    tremor = float(_feature_value(features, 'f0_tremor_intensity', 0))

    severe_pattern = (jitter >= 2.0 and shimmer >= 8.0 and hnr <= 12.0) or (tremor >= 55.0 and jitter >= 1.5)
    moderate_pattern = (jitter >= 1.5 and shimmer >= 6.0 and hnr <= 14.0) or (tremor >= 45.0)

    boosted = dict(scores)
    current = float(boosted.get('parkinsons', 0.0))
    if park_prob is not None:
        current = max(current, 0.6 * current + 0.4 * float(park_prob))

    if severe_pattern:
        current = max(current, 70.0)
    elif moderate_pattern:
        current = max(current, 55.0)

    boosted['parkinsons'] = current
    return _normalize_scores(boosted)


def _feature_value(features: Dict[str, Any], key: str, default: Number = 0) -> Number:
    """
    Read a feature with compatibility for sustained and sequence feature sets.

    Sequence analysis stores many values as `<name>_avg`; sustained stores `<name>`.
    """
    value = features.get(key)
    if value is None:
        value = features.get(f'{key}_avg', default)
    return value


def analyze_multi_disease(audio_path: str, test_type: str = 'sustained_vowel') -> Dict[str, Any]:
    """
    Comprehensive multi-disease analysis from voice recording

    Parameters:
    - audio_path: Path to audio file
    - test_type: 'sustained_vowel' or 'vowel_sequence'

    Returns:
    - Dictionary with disease probabilities, features, and recommendations
    """

    _load_model_assets()

    # Load audio
    y, sr = librosa.load(audio_path, sr=None)

    # Extract comprehensive features based on requested test mode.
    if test_type == 'vowel_sequence':
        features = analyze_vowel_sequence(y, sr)
    else:
        features = extract_vowel_features(y, sr, vowel_type='sustained')

    # Start with clinical rule-based scores.
    disease_scores = classify_disease_from_features(features)

    # Add trained multi-disease model scores when available.
    model_scores = _predict_multi_model_scores(features)
    if model_scores:
        merged = {}
        classes = set(disease_scores.keys()) | set(model_scores.keys())
        for cls in classes:
            merged[cls] = 0.45 * float(disease_scores.get(cls, 0.0)) + 0.55 * float(model_scores.get(cls, 0.0))
        disease_scores = _normalize_scores(merged)

    # Add dedicated Parkinson model signal from advanced feature set.
    advanced_features = extract_advanced_features(y, sr)
    parkinson_prob = _predict_parkinson_probability(advanced_features)
    disease_scores = _apply_parkinson_boost(disease_scores, features, parkinson_prob)

    # Sort diseases by probability
    sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)

    # Determine primary diagnosis
    primary_disease, primary_score = sorted_diseases[0]

    # Determine risk level
    if primary_disease == 'healthy':
        risk_level = 'low'
        overall_risk_score = int(round(100 - primary_score))
    else:
        overall_risk_score = int(round(primary_score))
        if primary_score >= 70:
            risk_level = 'high'
        elif primary_score >= 50:
            risk_level = 'moderate'
        else:
            risk_level = 'low'

    # Generate detailed results
    results = {
        'success': True,
        'test_type': test_type,
        'primary_diagnosis': {
            'disease': primary_disease,
            'disease_name': DISEASE_PROFILES[primary_disease]['name'] if primary_disease != 'healthy' else 'Healthy',
            'probability': round(primary_score, 1),
            'risk_level': risk_level,
            'category': DISEASE_PROFILES[primary_disease]['category'] if primary_disease != 'healthy' else None
        },
        'all_diseases': [
            {
                'disease': disease,
                'disease_name': DISEASE_PROFILES[disease]['name'] if disease != 'healthy' else 'Healthy',
                'probability': round(score, 1),
                'category': DISEASE_PROFILES[disease]['category'] if disease != 'healthy' else None
            }
            for disease, score in sorted_diseases
        ],
        'overall_risk_score': overall_risk_score,
        'key_features': {
            'f0_mean': round(_feature_value(features, 'f0_mean'), 2),
            'jitter_relative': round(_feature_value(features, 'jitter_relative'), 4),
            'shimmer_relative': round(_feature_value(features, 'shimmer_relative'), 4),
            'hnr': round(_feature_value(features, 'hnr'), 2),
            'f0_tremor_intensity': round(_feature_value(features, 'f0_tremor_intensity'), 2),
            'voice_breaks': _feature_value(features, 'num_voice_breaks'),
            'formant_f1': round(_feature_value(features, 'f1'), 2),
            'formant_f2': round(_feature_value(features, 'f2'), 2)
        },
        'biomarkers': get_disease_biomarkers(primary_disease, features),
        'recommendations': generate_recommendations(primary_disease, primary_score, risk_level),
        'specialist_needed': DISEASE_PROFILES[primary_disease]['specialists'] if primary_disease != 'healthy' else None
    }

    # Debug signals for transparency in tuning.
    results['model_signals'] = {
        'rule_based_used': True,
        'multi_disease_model_used': model_scores is not None,
        'parkinson_model_used': parkinson_prob is not None,
        'parkinson_model_probability': round(parkinson_prob, 2) if parkinson_prob is not None else None
    }

    return results


def get_disease_biomarkers(disease: str, features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract relevant biomarkers for detected disease"""
    if disease == 'healthy' or disease not in DISEASE_PROFILES:
        return []

    biomarkers = []
    key_features = DISEASE_PROFILES[disease]['key_biomarkers']

    biomarker_descriptions = {
        'f0_tremor_intensity': {
            'name': 'Voice Tremor Intensity',
            'normal_range': '< 50',
            'unit': 'Hz',
            'clinical_significance': 'Indicates involuntary oscillation in vocal cords'
        },
        'jitter_relative': {
            'name': 'Pitch Variation (Jitter)',
            'normal_range': '< 1.0%',
            'unit': '%',
            'clinical_significance': 'Measures cycle-to-cycle pitch instability'
        },
        'shimmer_relative': {
            'name': 'Amplitude Variation (Shimmer)',
            'normal_range': '< 5.0%',
            'unit': '%',
            'clinical_significance': 'Measures voice loudness fluctuation'
        },
        'hnr': {
            'name': 'Harmonic-to-Noise Ratio',
            'normal_range': '> 15 dB',
            'unit': 'dB',
            'clinical_significance': 'Indicates voice quality and breathiness'
        },
        'num_voice_breaks': {
            'name': 'Voice Breaks/Pauses',
            'normal_range': '< 2',
            'unit': 'count',
            'clinical_significance': 'Indicates speech fluency issues'
        },
        'max_pause_duration': {
            'name': 'Maximum Pause Duration',
            'normal_range': '< 1.0 sec',
            'unit': 'seconds',
            'clinical_significance': 'Indicates word-finding difficulties'
        },
        'rms_energy_mean': {
            'name': 'Voice Intensity',
            'normal_range': '> 0.01',
            'unit': 'amplitude',
            'clinical_significance': 'Indicates muscle strength and breath support'
        },
        'formant_transition_smoothness': {
            'name': 'Articulation Smoothness',
            'normal_range': '< 300 Hz',
            'unit': 'Hz',
            'clinical_significance': 'Indicates motor coordination for speech'
        },
        'formant_dispersion': {
            'name': 'Vowel Space Area',
            'normal_range': '800-1500 Hz',
            'unit': 'Hz',
            'clinical_significance': 'Indicates articulation clarity'
        },
        'energy_entropy': {
            'name': 'Voice Energy Entropy',
            'normal_range': '< 4.0',
            'unit': 'entropy',
            'clinical_significance': 'Indicates voice stability and control'
        },
        'spectral_flux': {
            'name': 'Spectral Change Rate',
            'normal_range': '> 15',
            'unit': 'flux',
            'clinical_significance': 'Indicates voice dynamics and variability'
        },
        'f0_transition_smoothness': {
            'name': 'Pitch Transition Smoothness',
            'normal_range': '< 30 Hz',
            'unit': 'Hz',
            'clinical_significance': 'Indicates pitch control coordination'
        },
        'zcr_mean': {
            'name': 'Zero Crossing Rate',
            'normal_range': '< 0.15',
            'unit': 'rate',
            'clinical_significance': 'Indicates voice noisiness and breathiness'
        }
    }

    for feature_key in key_features:
        if feature_key in biomarker_descriptions:
            info = biomarker_descriptions[feature_key]
            value = _feature_value(features, feature_key)

            biomarkers.append({
                'name': info['name'],
                'value': round(value, 3) if isinstance(value, (int, float)) else value,
                'unit': info['unit'],
                'normal_range': info['normal_range'],
                'clinical_significance': info['clinical_significance']
            })

    return biomarkers


def generate_recommendations(disease: str, probability: float, risk_level: str) -> List[str]:
    """Generate personalized recommendations based on diagnosis"""
    recommendations = []

    if disease == 'healthy':
        recommendations = [
            'Your voice patterns appear normal',
            'Continue with regular health monitoring',
            'Repeat screening annually or if symptoms develop',
            'Maintain vocal health through adequate hydration'
        ]
    elif risk_level == 'low':
        recommendations = [
            f'Mild indicators of {DISEASE_PROFILES[disease]["name"]} detected',
            'Monitor symptoms and track changes over time',
            'Consider lifestyle modifications and vocal exercises',
            'Schedule follow-up screening in 3-6 months',
            'Consult your primary care physician if symptoms worsen'
        ]
    elif risk_level == 'moderate':
        recommendations = [
            f'Moderate indicators of {DISEASE_PROFILES[disease]["name"]} detected',
            'Consultation with a neurologist is recommended',
            'Keep a symptom diary to track progression',
            'Consider comprehensive neurological evaluation',
            'Early intervention can significantly improve outcomes'
        ]
    else:  # high risk
        recommendations = [
            f'Strong indicators of {DISEASE_PROFILES[disease]["name"]} detected',
            'URGENT: Schedule consultation with a specialist immediately',
            'Comprehensive neurological examination strongly recommended',
            'Consider imaging studies (MRI, CT) as advised by neurologist',
            'Early diagnosis and treatment are critical for best outcomes',
            'Bring voice analysis results to your appointment'
        ]

    # Disease-specific recommendations
    if disease == 'parkinsons':
        recommendations.append('Consider: LSVT LOUD voice therapy, regular exercise, Mediterranean diet')
    elif disease == 'alzheimers':
        recommendations.append('Consider: Cognitive stimulation, memory exercises, social engagement')
    elif disease == 'als':
        recommendations.append('Consider: Speech therapy, breathing exercises, nutritional support')
    elif disease == 'multiple_sclerosis':
        recommendations.append('Consider: Physical therapy, stress management, vitamin D supplementation')
    elif disease == 'stroke':
        recommendations.append('Consider: Speech-language pathology, swallowing assessment, rehabilitation')

    return recommendations


def get_recording_instructions(test_type: str = 'sustained_vowel') -> Dict[str, Any]:
    """Get instructions for voice recording based on test type"""

    instructions = {
        'sustained_vowel': {
            'title': 'Sustained Vowel Test',
            'duration': '5-10 seconds',
            'steps': [
                'Find a quiet room with minimal background noise',
                'Position microphone 6-8 inches from your mouth',
                'Take a comfortable deep breath',
                'Choose ONE vowel: /a/ (as in "father"), /e/ (as in "see"), or /i/ (as in "me")',
                'Say the vowel sound at your natural speaking pitch',
                'Hold the sound steadily for 5-10 seconds',
                'Keep volume consistent throughout',
                'Stop recording when finished'
            ],
            'tips': [
                'Don\'t force your voice - use comfortable volume',
                'Avoid voice cracks or sudden pitch changes',
                'If you need to breathe, stop and start a new recording',
                'Practice once or twice before the final recording'
            ],
            'example': 'AAAAAAAAAA (steady, 5-10 seconds)'
        },
        'vowel_sequence': {
            'title': 'Vowel Sequence Test',
            'duration': '10-15 seconds',
            'steps': [
                'Find a quiet room with minimal background noise',
                'Position microphone 6-8 inches from your mouth',
                'Say all five vowels in sequence with brief pauses:',
                '/a/ (father) - 2 seconds',
                '/e/ (see) - 2 seconds',
                '/i/ (me) - 2 seconds',
                '/o/ (go) - 2 seconds',
                '/u/ (you) - 2 seconds',
                'Keep consistent volume for all vowels',
                'Pause briefly (0.5 sec) between each vowel'
            ],
            'tips': [
                'This test evaluates articulation and coordination',
                'Try to keep pitch and loudness similar across vowels',
                'Brief pauses help separate vowels for analysis',
                'Complete the full sequence without stopping'
            ],
            'example': 'AAA [pause] EEE [pause] III [pause] OOO [pause] UUU'
        },
        'sentence_reading': {
            'title': 'Sentence Reading Test',
            'duration': '30-60 seconds',
            'steps': [
                'Read the following passage at natural speaking pace:',
                '"The quick brown fox jumps over the lazy dog. Peter Piper picked a peck of pickled peppers. She sells seashells by the seashore."',
                'Speak clearly and naturally',
                'Don\'t rush - use your normal reading speed',
                'Complete all sentences'
            ],
            'tips': [
                'This test evaluates fluency and articulation',
                'Natural speech is more diagnostic than careful speech',
                'Pauses and hesitations are normal and informative',
                'Don\'t worry about perfect pronunciation'
            ],
            'example': 'Natural reading voice, not performance voice'
        }
    }

    return instructions.get(test_type, instructions['sustained_vowel'])


# Disease-specialist mapping for booking system
def get_specialists_for_disease(disease: str) -> List[str]:
    """Get recommended specialist types for a disease"""
    if disease in DISEASE_PROFILES:
        return DISEASE_PROFILES[disease]['specialists']
    return ['General Neurologist']


def get_disease_description(disease: str) -> Optional[Dict[str, str]]:
    """Get clinical description of disease"""
    if disease in DISEASE_PROFILES:
        return {
            'name': DISEASE_PROFILES[disease]['name'],
            'category': DISEASE_PROFILES[disease]['category'],
            'description': DISEASE_PROFILES[disease]['description']
        }
    return None
