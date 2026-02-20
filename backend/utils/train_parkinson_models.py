"""Train Parkinson's voice detection models using HC/PD recordings."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

import joblib
import librosa
import matplotlib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from advanced_features import extract_advanced_features
from vowel_analysis import classify_disease_from_features, extract_vowel_features

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RANDOM_STATE = 42
TARGET_SAMPLE_RATE = 22050
POSITIVE_LABEL = "parkinsons"
NEGATIVE_LABEL = "healthy"


@dataclass
class ModelMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float | None


def _resolve_dirs(base_dir: Path, names: list[str]) -> list[Path]:
    matches: list[Path] = []
    for name in names:
        candidate = base_dir / name
        if candidate.exists() and candidate.is_dir():
            matches.append(candidate)
    if matches:
        return matches

    lower_names = {name.lower() for name in names}
    for child in sorted(base_dir.iterdir()):
        if child.is_dir() and child.name.lower() in lower_names:
            matches.append(child)

    if not matches:
        raise FileNotFoundError(f"Could not find expected directory in {base_dir}: {names}")
    return matches


def _iter_audio_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.wav") if path.is_file())


def _safe_float(value: Any) -> float:
    try:
        value = float(value)
        if np.isnan(value) or np.isinf(value):
            return 0.0
        return value
    except (TypeError, ValueError):
        return 0.0


def build_dataset(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    healthy_dirs = _resolve_dirs(data_dir, ["HC", "HC_AH"])
    parkinson_dirs = _resolve_dirs(data_dir, ["PD", "PD_AH"])

    file_map = {
        NEGATIVE_LABEL: [path for directory in healthy_dirs for path in _iter_audio_files(directory)],
        POSITIVE_LABEL: [path for directory in parkinson_dirs for path in _iter_audio_files(directory)],
    }

    rows: list[dict[str, Any]] = []
    indicator_rows: list[dict[str, Any]] = []

    for label, files in file_map.items():
        for audio_path in files:
            y, sr = librosa.load(str(audio_path), sr=TARGET_SAMPLE_RATE)
            advanced_features = extract_advanced_features(y, sr)

            row: dict[str, Any] = {
                key: _safe_float(value) for key, value in advanced_features.items()
            }
            row["filename"] = audio_path.name
            row["label"] = label
            rows.append(row)

            vowel_features = extract_vowel_features(y, sr, vowel_type="sustained")
            disease_scores = classify_disease_from_features(vowel_features)
            indicator_row = {
                "filename": audio_path.name,
                "label": label,
            }
            for key, value in disease_scores.items():
                indicator_row[f"indicator_{key}"] = _safe_float(value)
            indicator_rows.append(indicator_row)

    if not rows:
        raise ValueError(f"No .wav files found under {data_dir}")

    features_df = pd.DataFrame(rows).fillna(0.0)
    indicators_df = pd.DataFrame(indicator_rows).fillna(0.0)
    return features_df, indicators_df


def _parkinson_probability(model: Any, X: np.ndarray) -> np.ndarray:
    probs = model.predict_proba(X)
    classes = [str(item).lower() for item in model.classes_]
    if POSITIVE_LABEL in classes:
        return probs[:, classes.index(POSITIVE_LABEL)]
    if "1" in classes:
        return probs[:, classes.index("1")]
    return probs[:, -1]


def _evaluate_model(model: Any, X_test: np.ndarray, y_test: pd.Series) -> tuple[ModelMetrics, np.ndarray, np.ndarray]:
    y_pred = model.predict(X_test)
    y_prob = _parkinson_probability(model, X_test)
    y_true_binary = (y_test == POSITIVE_LABEL).astype(int)

    roc_auc: float | None = None
    if len(np.unique(y_true_binary)) > 1:
        roc_auc = float(roc_auc_score(y_true_binary, y_prob))

    metrics = ModelMetrics(
        accuracy=float(accuracy_score(y_test, y_pred)),
        precision=float(precision_score(y_test, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)),
        recall=float(recall_score(y_test, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)),
        f1=float(f1_score(y_test, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)),
        roc_auc=roc_auc,
    )
    return metrics, y_pred, y_prob


def _save_confusion_matrix(y_true: pd.Series, y_pred: np.ndarray, out_path: Path) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=[NEGATIVE_LABEL, POSITIVE_LABEL])
    disp = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=[NEGATIVE_LABEL, POSITIVE_LABEL],
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Parkinson's Detection - Confusion Matrix")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _save_feature_importance(model: Pipeline, feature_names: list[str], out_path: Path) -> None:
    classifier = model.named_steps["classifier"]
    importances = classifier.feature_importances_
    importance_df = pd.DataFrame(
        {"feature": feature_names, "importance": importances}
    ).sort_values("importance", ascending=False)
    top_df = importance_df.head(20).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top_df["feature"], top_df["importance"], color="#1f77b4")
    ax.set_title("Top 20 Random Forest Feature Importances")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _save_roc_curve(
    y_test: pd.Series,
    model_probs: dict[str, np.ndarray],
    out_path: Path,
) -> None:
    y_true_binary = (y_test == POSITIVE_LABEL).astype(int).to_numpy()
    if len(np.unique(y_true_binary)) < 2:
        return

    fig, ax = plt.subplots(figsize=(7, 6))
    for name, probs in model_probs.items():
        fpr, tpr, _ = roc_curve(y_true_binary, probs)
        auc_score = roc_auc_score(y_true_binary, probs)
        ax.plot(fpr, tpr, linewidth=2, label=f"{name} (AUC={auc_score:.3f})")

    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1.5)
    ax.set_title("ROC Curve - Parkinson's Voice Detection")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def train_models(
    data_dir: Path,
    models_dir: Path,
    visualizations_dir: Path,
    temp_dir: Path,
) -> dict[str, Any]:
    models_dir.mkdir(parents=True, exist_ok=True)
    visualizations_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    features_df, indicators_df = build_dataset(data_dir)

    feature_names = [col for col in features_df.columns if col not in {"filename", "label"}]
    X = features_df[feature_names].astype(float).fillna(0.0).to_numpy()
    y = features_df["label"].astype(str)

    X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
        X,
        y,
        np.arange(len(X)),
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    rf_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
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
        ]
    )
    rf_model.fit(X_train, y_train)

    svm_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                SVC(
                    C=4.0,
                    kernel="rbf",
                    gamma="scale",
                    class_weight="balanced",
                    probability=True,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    svm_model.fit(X_train, y_train)

    ensemble_model = VotingClassifier(
        estimators=[
            ("rf", rf_model),
            ("svm", svm_model),
        ],
        voting="soft",
        weights=[0.55, 0.45],
        n_jobs=-1,
    )
    ensemble_model.fit(X_train, y_train)

    rf_metrics, rf_pred, rf_probs = _evaluate_model(rf_model, X_test, y_test)
    svm_metrics, svm_pred, svm_probs = _evaluate_model(svm_model, X_test, y_test)
    ensemble_metrics, ensemble_pred, ensemble_probs = _evaluate_model(ensemble_model, X_test, y_test)

    _save_feature_importance(
        rf_model,
        feature_names,
        visualizations_dir / "feature_importance.png",
    )
    _save_roc_curve(
        y_test,
        {
            "Random Forest": rf_probs,
            "SVM": svm_probs,
            "Ensemble": ensemble_probs,
        },
        visualizations_dir / "roc_curve.png",
    )

    model_registry: dict[str, tuple[Any, ModelMetrics]] = {
        "random_forest": (rf_model, rf_metrics),
        "svm": (svm_model, svm_metrics),
        "ensemble": (ensemble_model, ensemble_metrics),
    }

    def _score_key(item: tuple[str, tuple[Any, ModelMetrics]]) -> tuple[float, float, float]:
        _, (_, model_metrics) = item
        roc = model_metrics.roc_auc if model_metrics.roc_auc is not None else -1.0
        return (roc, model_metrics.f1, model_metrics.accuracy)

    selected_model_name, (selected_model, _) = max(model_registry.items(), key=_score_key)
    prediction_registry = {
        "random_forest": rf_pred,
        "svm": svm_pred,
        "ensemble": ensemble_pred,
    }
    _save_confusion_matrix(
        y_test,
        prediction_registry[selected_model_name],
        visualizations_dir / "confusion_matrix.png",
    )

    # Core model artifacts
    joblib.dump(rf_model, models_dir / "parkinson_rf_model.pkl")
    joblib.dump(svm_model, models_dir / "parkinson_svm_model.pkl")
    joblib.dump(ensemble_model, models_dir / "parkinson_ensemble_model.pkl")
    joblib.dump(selected_model, models_dir / "parkinson_model.pkl")

    # Compatibility artifacts for existing inference.
    (models_dir / "feature_names.txt").write_text("\n".join(feature_names), encoding="utf-8")
    features_df.to_csv(models_dir / "extracted_features.csv", index=False)

    metadata = {
        "model_type": "rf_svm_soft_voting",
        "dataset": {
            "total_samples": int(len(features_df)),
            "train_samples": int(len(train_idx)),
            "test_samples": int(len(test_idx)),
            "class_distribution": {
                str(label): int(count) for label, count in y.value_counts().to_dict().items()
            },
            "sample_rate": TARGET_SAMPLE_RATE,
        },
        "metrics": {
            "random_forest": rf_metrics.__dict__,
            "svm": svm_metrics.__dict__,
            "ensemble": ensemble_metrics.__dict__,
        },
        "selected_model": selected_model_name,
        "features": {
            "count": len(feature_names),
            "names_file": "feature_names.txt",
        },
        "artifacts": {
            "selected_model": "parkinson_model.pkl",
            "random_forest_model": "parkinson_rf_model.pkl",
            "svm_model": "parkinson_svm_model.pkl",
            "voting_ensemble_model": "parkinson_ensemble_model.pkl",
            "dataset_csv": "extracted_features.csv",
            "feature_importance_plot": "feature_importance.png",
            "confusion_matrix_plot": "confusion_matrix.png",
            "roc_curve_plot": "roc_curve.png",
        },
        "trained_at": datetime.now(UTC).isoformat(),
    }
    (models_dir / "parkinson_model_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    # Intermediate files in temp/
    split_df = features_df[["filename", "label"]].copy()
    split_df["split"] = "train"
    split_df.loc[test_idx, "split"] = "test"
    split_df.to_csv(temp_dir / "parkinson_training_split.csv", index=False)
    indicators_df.to_csv(temp_dir / "parkinson_biomarker_indicators.csv", index=False)
    (temp_dir / "parkinson_training_report.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    return metadata


def parse_args() -> argparse.Namespace:
    backend_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Train Parkinson's voice detection models.")
    parser.add_argument("--data-dir", type=Path, default=backend_root / "data")
    parser.add_argument("--models-dir", type=Path, default=backend_root / "models")
    parser.add_argument("--visualizations-dir", type=Path, default=backend_root / "visualizations")
    parser.add_argument("--temp-dir", type=Path, default=backend_root / "temp")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = train_models(
        data_dir=args.data_dir,
        models_dir=args.models_dir,
        visualizations_dir=args.visualizations_dir,
        temp_dir=args.temp_dir,
    )
    selected_model_name = metadata["selected_model"]
    selected_metrics = metadata["metrics"][selected_model_name]
    print("Training complete.")
    print(f"Selected model: {selected_model_name}")
    print(f"Accuracy: {selected_metrics['accuracy']:.4f}")
    print(f"F1: {selected_metrics['f1']:.4f}")
    print(f"ROC-AUC: {selected_metrics['roc_auc']}")


if __name__ == "__main__":
    main()
