"""Audio processing service."""

from datetime import datetime
from pathlib import Path

from fastapi import UploadFile
import librosa
from librosa import display as librosa_display
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from app.core.config import settings
from app.schemas.audio import TestType
from app.utils.validators import validate_extension
from app.utils.vowel_analysis import extract_features_by_test_type


class AudioProcessor:
    def __init__(self) -> None:
        self.temp_dir = settings.temp_full_path
        self.upload_dir = settings.upload_full_path
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> Path:
        if not file.filename:
            raise ValueError("No file selected")

        validate_extension(file.filename)

        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            raise ValueError(f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB")

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(file.filename).name}"
        target = self.upload_dir / filename
        target.write_bytes(content)
        return target

    def extract_features(self, audio_path: Path, test_type: TestType) -> tuple[np.ndarray, int, dict]:
        y, sr = librosa.load(str(audio_path), sr=22050)
        duration = len(y) / sr
        if duration < settings.MIN_AUDIO_DURATION:
            raise ValueError(f"Audio too short: {duration:.1f}s")
        if duration > settings.MAX_AUDIO_DURATION:
            raise ValueError(f"Audio too long: {duration:.1f}s")

        features = extract_features_by_test_type(y, sr, test_type.value)
        return y, sr, features

    def generate_visualizations(self, y: np.ndarray, sr: int, timestamp: str) -> dict:
        waveform_path = self.temp_dir / "waveform.png"
        spectrogram_path = self.temp_dir / "spectrogram.png"

        plt.figure(figsize=(12, 4))
        plt.plot(np.linspace(0, len(y) / sr, len(y)), y)
        plt.title("Audio Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.savefig(waveform_path)
        plt.close()

        plt.figure(figsize=(12, 6))
        d_spec = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        librosa_display.specshow(d_spec, sr=sr, x_axis="time", y_axis="log")
        plt.colorbar(format="%+2.0f dB")
        plt.title("Spectrogram")
        plt.tight_layout()
        plt.savefig(spectrogram_path)
        plt.close()

        return {
            "waveform_url": f"/api/temp/waveform.png?t={timestamp}",
            "spectrogram_url": f"/api/temp/spectrogram.png?t={timestamp}",
        }
