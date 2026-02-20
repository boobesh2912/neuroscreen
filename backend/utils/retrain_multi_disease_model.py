"""Retrain the multi-disease model artifact using current sklearn version."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

import joblib
import librosa
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

from vowel_analysis import extract_vowel_features

RANDOM_STATE = 42
TARGET_SAMPLE_RATE = 22050
SYNTHETIC_PER_CLASS = 200
DISEASE_CLASSES = [
    "als",
    "alzheimers",
    "healthy",
    "multiple_sclerosis",
    "parkinsons",
    "stroke",
]


def _iter_wavs(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("*.wav") if path.is_file())


def _safe_float(value: Any) -> float:
    try:
        f = float(value)
        if not np.isfinite(f):
            return 0.0
        return f
    except (TypeError, ValueError):
        return 0.0


def _load_feature_names(models_dir: Path) -> list[str]:
    artifact_path = models_dir / "multi_disease_model_optimized.pkl"
    if artifact_path.exists():
        artifact = joblib.load(artifact_path)
        if isinstance(artifact, dict):
            names = artifact.get("feature_names")
            if isinstance(names, list) and names:
                return [str(name) for name in names]
    return []


def _extract_base_features(data_dir: Path) -> list[dict[str, float]]:
    healthy_dir = data_dir / "HC_AH"
    pd_dir = data_dir / "PD_AH"
    files = _iter_wavs(healthy_dir) + _iter_wavs(pd_dir)
    if not files:
        raise ValueError(f"No wav files found in {data_dir}")

    base: list[dict[str, float]] = []
    for path in files:
        y, sr = librosa.load(str(path), sr=TARGET_SAMPLE_RATE)
        features = extract_vowel_features(y, sr, vowel_type="sustained")
        base.append({k: _safe_float(v) for k, v in features.items()})
    return base


def _noise_scale(name: str) -> float:
    if name.startswith("mfcc_"):
        return 0.04
    if name in {"f0_mean", "f0_std", "f0_range", "f1", "f2", "f3"}:
        return 0.05
    if name in {"jitter_relative", "shimmer_relative", "hnr", "spectral_flux"}:
        return 0.08
    return 0.06


def _apply_profile(features: dict[str, float], disease: str, rng: np.random.Generator) -> dict[str, float]:
    result = dict(features)

    def set_scaled(key: str, factor: float, minimum: float | None = None, maximum: float | None = None) -> None:
        base = _safe_float(result.get(key, 0.0))
        value = base * factor
        if minimum is not None:
            value = max(value, minimum)
        if maximum is not None:
            value = min(value, maximum)
        result[key] = value

    if disease == "parkinsons":
        set_scaled("f0_tremor_intensity", 1.8, minimum=55.0)
        set_scaled("jitter_relative", 1.9, minimum=1.8)
        set_scaled("shimmer_relative", 1.7, minimum=7.0)
        set_scaled("hnr", 0.72, maximum=13.5)
    elif disease == "alzheimers":
        set_scaled("num_voice_breaks", 2.5, minimum=4.0)
        set_scaled("max_pause_duration", 2.2, minimum=2.2)
        set_scaled("energy_entropy", 1.6, minimum=5.2)
        set_scaled("avg_segment_duration", 1.35)
    elif disease == "als":
        set_scaled("rms_energy_mean", 0.35, maximum=0.009)
        set_scaled("shimmer_relative", 1.9, minimum=8.5)
        set_scaled("spectral_flux", 0.45, maximum=8.5)
        set_scaled("hnr", 0.8)
    elif disease == "multiple_sclerosis":
        set_scaled("formant_transition_smoothness", 2.6, minimum=550.0)
        set_scaled("f0_transition_smoothness", 2.0, minimum=55.0)
        set_scaled("articulation_rate", 0.75)
    elif disease == "stroke":
        set_scaled("formant_dispersion", 0.45, maximum=420.0)
        set_scaled("zcr_mean", 1.8, minimum=0.22)
        set_scaled("spectral_bandwidth_mean", 1.25)
    elif disease == "healthy":
        set_scaled("f0_tremor_intensity", 0.6, maximum=35.0)
        set_scaled("jitter_relative", 0.45, maximum=0.8)
        set_scaled("shimmer_relative", 0.55, maximum=4.0)
        set_scaled("hnr", 1.15, minimum=16.5)
        set_scaled("num_voice_breaks", 0.35, maximum=2.0)
        set_scaled("max_pause_duration", 0.45, maximum=1.0)

    for key, value in list(result.items()):
        sigma = _noise_scale(key)
        noisy = value * (1.0 + rng.normal(0.0, sigma))
        if key in {"hnr"}:
            noisy = max(-20.0, noisy)
        else:
            noisy = max(0.0, noisy)
        result[key] = _safe_float(noisy)

    return result


def _build_synthetic_dataset(
    base_features: list[dict[str, float]],
    feature_names: list[str],
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.Series]:
    rows: list[dict[str, float]] = []
    labels: list[str] = []

    for disease in DISEASE_CLASSES:
        for _ in range(SYNTHETIC_PER_CLASS):
            source = dict(base_features[rng.integers(0, len(base_features))])
            transformed = _apply_profile(source, disease, rng)
            rows.append({name: _safe_float(transformed.get(name, 0.0)) for name in feature_names})
            labels.append(disease)

    X = pd.DataFrame(rows, columns=feature_names).fillna(0.0)
    y = pd.Series(labels, name="label")
    return X, y


def retrain_and_save() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    models_dir = backend_dir / "models"
    data_dir = backend_dir / "data"
    temp_dir = backend_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    old_model_path = models_dir / "multi_disease_model_optimized.pkl"
    backup_path = temp_dir / "multi_disease_model_optimized_backup.pkl"
    if old_model_path.exists():
        backup_path.write_bytes(old_model_path.read_bytes())

    feature_names = _load_feature_names(models_dir)
    if not feature_names:
        base = _extract_base_features(data_dir)
        feature_names = sorted(base[0].keys())

    base_features = _extract_base_features(data_dir)
    rng = np.random.default_rng(RANDOM_STATE)
    X, y = _build_synthetic_dataset(base_features, feature_names, rng)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_encoded,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_full_scaled = scaler.transform(X)

    model = VotingClassifier(
        estimators=[
            (
                "rf",
                RandomForestClassifier(
                    n_estimators=400,
                    max_depth=None,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=(128, 64),
                    activation="relu",
                    alpha=1e-4,
                    learning_rate_init=1e-3,
                    max_iter=500,
                    random_state=RANDOM_STATE,
                ),
            ),
        ],
        voting="soft",
        weights=[0.6, 0.4],
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    train_accuracy = float(accuracy_score(y_train, model.predict(X_train_scaled)))
    test_accuracy = float(accuracy_score(y_test, model.predict(X_test_scaled)))

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(model, X_full_scaled, y_encoded, cv=cv, scoring="accuracy", n_jobs=1)

    classes = [str(cls) for cls in label_encoder.classes_]
    artifact = {
        "model_type": "ensemble",
        "model": model,
        "scaler": scaler,
        "label_encoder": label_encoder,
        "feature_names": feature_names,
        "classes": classes,
        "training_history": {
            "model_type": "ensemble",
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "cv_accuracy_mean": float(np.mean(cv_scores)),
            "cv_accuracy_std": float(np.std(cv_scores)),
            "classes": classes,
            "n_features": len(feature_names),
            "n_samples": int(len(X)),
            "class_distribution": dict(Counter(y.tolist())),
            "trained_at": datetime.now(UTC).isoformat(),
            "sklearn_retrained": True,
        },
    }

    joblib.dump(artifact, old_model_path)

    metadata_path = models_dir / "multi_disease_model_optimized_metadata.json"
    metadata_path.write_text(
        json.dumps(artifact["training_history"], indent=2),
        encoding="utf-8",
    )

    summary_path = temp_dir / "multi_disease_retrain_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "model_path": str(old_model_path),
                "backup_path": str(backup_path) if backup_path.exists() else None,
                "classes": classes,
                "train_accuracy": train_accuracy,
                "test_accuracy": test_accuracy,
                "cv_accuracy_mean": float(np.mean(cv_scores)),
                "cv_accuracy_std": float(np.std(cv_scores)),
                "n_samples": int(len(X)),
                "n_features": len(feature_names),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Retrained multi-disease model in current sklearn version.")
    print(f"Saved: {old_model_path}")
    print(f"Backup: {backup_path if backup_path.exists() else 'not-created'}")
    print(f"Train acc: {train_accuracy:.4f}")
    print(f"Test acc: {test_accuracy:.4f}")
    print(f"CV acc mean/std: {float(np.mean(cv_scores)):.4f} / {float(np.std(cv_scores)):.4f}")


if __name__ == "__main__":
    retrain_and_save()
