"""
Vowel-Specific Analysis for Multi-Disease Detection
Extracts clinical biomarkers from sustained vowel sounds for neurological disorder screening

Supported vowel phonations:
- /a/ (as in "father") - General voice quality
- /e/ (as in "see") - High-frequency analysis
- /i/ (as in "me") - Resonance patterns
- /o/ (as in "go") - Mid-frequency stability
- /u/ (as in "you") - Low-frequency patterns

Clinical Applications:
- Parkinson's Disease: Tremor in voice, reduced loudness
- Alzheimer's Disease: Hesitations, word-finding difficulties
- ALS: Progressive muscle weakness, slurred speech
- Multiple Sclerosis: Scanning speech, coordination issues
- Stroke/Aphasia: Speech impediments, articulation problems
"""

import numpy as np
import librosa
from scipy import signal
from scipy.stats import skew, kurtosis

def extract_vowel_features(y, sr, vowel_type='sustained'):
    """
    Extract comprehensive vowel-specific features for disease detection

    Parameters:
    - y: audio time series
    - sr: sampling rate
    - vowel_type: 'sustained' (single vowel) or 'sequence' (multiple vowels)

    Returns:
    - Dictionary of 100+ vowel-specific features
    """
    features = {}

    # ===================================================================
    # 1. FUNDAMENTAL FREQUENCY (F0) ANALYSIS
    # ===================================================================
    f0 = librosa.yin(y, fmin=50, fmax=400, sr=sr)
    f0_voiced = f0[f0 > 0]

    if len(f0_voiced) > 0:
        features['f0_mean'] = float(np.mean(f0_voiced))
        features['f0_std'] = float(np.std(f0_voiced))
        features['f0_min'] = float(np.min(f0_voiced))
        features['f0_max'] = float(np.max(f0_voiced))
        features['f0_range'] = features['f0_max'] - features['f0_min']
        features['f0_median'] = float(np.median(f0_voiced))
        features['f0_skewness'] = float(skew(f0_voiced))
        features['f0_kurtosis'] = float(kurtosis(f0_voiced))

        # F0 tremor (important for Parkinson's detection)
        # Use FFT frequency bins (Hz) and guard against empty masks.
        f0_tremor_spectrum = np.abs(np.fft.rfft(f0_voiced))
        f0_tremor_freqs = np.fft.rfftfreq(len(f0_voiced), d=1.0 / sr)
        tremor_mask = (f0_tremor_freqs >= 4.0) & (f0_tremor_freqs <= 8.0)  # 4-8 Hz
        if np.any(tremor_mask):
            features['f0_tremor_intensity'] = float(np.mean(f0_tremor_spectrum[tremor_mask]))
        else:
            features['f0_tremor_intensity'] = 0.0
    else:
        for key in ['f0_mean', 'f0_std', 'f0_min', 'f0_max', 'f0_range',
                    'f0_median', 'f0_skewness', 'f0_kurtosis', 'f0_tremor_intensity']:
            features[key] = 0.0

    # ===================================================================
    # 2. JITTER (Pitch Perturbation) - Key for Parkinson's/ALS
    # ===================================================================
    if len(f0_voiced) > 1:
        # Absolute jitter (cycle-to-cycle variation)
        f0_diff = np.abs(np.diff(f0_voiced))
        features['jitter_absolute'] = float(np.mean(f0_diff))
        features['jitter_relative'] = float(features['jitter_absolute'] / features['f0_mean'] * 100) if features['f0_mean'] > 0 else 0.0

        # Jitter ratio
        features['jitter_ppq5'] = float(np.mean(np.abs(f0_voiced[:-5] - f0_voiced[5:]))) if len(f0_voiced) > 5 else 0.0
        features['jitter_rap'] = float(np.mean(np.abs(f0_voiced[:-2] - f0_voiced[2:]))) if len(f0_voiced) > 2 else 0.0
    else:
        features['jitter_absolute'] = 0.0
        features['jitter_relative'] = 0.0
        features['jitter_ppq5'] = 0.0
        features['jitter_rap'] = 0.0

    # ===================================================================
    # 3. SHIMMER (Amplitude Perturbation) - Key for Voice Quality
    # ===================================================================
    amplitude_envelope = np.abs(librosa.stft(y))
    amplitude_mean = np.mean(amplitude_envelope, axis=0)

    if len(amplitude_mean) > 1:
        amp_diff = np.abs(np.diff(amplitude_mean))
        features['shimmer_absolute'] = float(np.mean(amp_diff))
        features['shimmer_relative'] = float(features['shimmer_absolute'] / np.mean(amplitude_mean) * 100) if np.mean(amplitude_mean) > 0 else 0.0
        features['shimmer_apq3'] = float(np.mean(np.abs(amplitude_mean[:-3] - amplitude_mean[3:]))) if len(amplitude_mean) > 3 else 0.0
        features['shimmer_apq5'] = float(np.mean(np.abs(amplitude_mean[:-5] - amplitude_mean[5:]))) if len(amplitude_mean) > 5 else 0.0
    else:
        features['shimmer_absolute'] = 0.0
        features['shimmer_relative'] = 0.0
        features['shimmer_apq3'] = 0.0
        features['shimmer_apq5'] = 0.0

    # ===================================================================
    # 4. HARMONIC-TO-NOISE RATIO (HNR) - Voice Quality Indicator
    # ===================================================================
    # Higher HNR = clearer voice; Lower HNR = breathier, hoarse voice
    harmonic = librosa.effects.harmonic(y)
    noise = y - harmonic

    harmonic_power = np.sum(harmonic ** 2)
    noise_power = np.sum(noise ** 2)

    if noise_power > 0:
        features['hnr'] = float(10 * np.log10(harmonic_power / noise_power))
    else:
        features['hnr'] = 20.0  # Very high HNR if no noise

    # ===================================================================
    # 5. FORMANT FREQUENCIES (F1, F2, F3) - Vowel Identification
    # ===================================================================
    # Formants are resonance frequencies unique to each vowel
    # Critical for detecting articulation disorders

    # Linear Predictive Coding (LPC) for formant estimation
    try:
        lpc_order = min(int(sr / 1000) + 2, 16)  # Typical: 8-16
        lpc_coeffs = librosa.lpc(y + 1e-10, order=lpc_order)
        roots = np.roots(lpc_coeffs)
        roots = roots[np.imag(roots) >= 0]

        # Convert to frequencies
        angles = np.arctan2(np.imag(roots), np.real(roots))
        freqs = sorted(angles * (sr / (2 * np.pi)))

        # Extract first 3 formants (F1, F2, F3)
        formants = [f for f in freqs if 50 < f < 5000][:3]

        features['f1'] = float(formants[0]) if len(formants) > 0 else 0.0
        features['f2'] = float(formants[1]) if len(formants) > 1 else 0.0
        features['f3'] = float(formants[2]) if len(formants) > 2 else 0.0

        # Formant variability (important for coordination disorders like MS)
        if len(formants) >= 2:
            features['formant_dispersion'] = float(formants[1] - formants[0])
        else:
            features['formant_dispersion'] = 0.0
    except:
        features['f1'] = 0.0
        features['f2'] = 0.0
        features['f3'] = 0.0
        features['formant_dispersion'] = 0.0

    # ===================================================================
    # 6. SPECTRAL FEATURES - Overall Voice Character
    # ===================================================================
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]

    features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
    features['spectral_centroid_std'] = float(np.std(spectral_centroids))
    features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
    features['spectral_rolloff_std'] = float(np.std(spectral_rolloff))
    features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
    features['spectral_bandwidth_std'] = float(np.std(spectral_bandwidth))

    # Spectral flux (rate of spectral change - important for tremor detection)
    spec = np.abs(librosa.stft(y))
    spec_diff = np.diff(spec, axis=1)
    features['spectral_flux'] = float(np.mean(np.sqrt(np.sum(spec_diff**2, axis=0))))

    # ===================================================================
    # 7. MFCC (Mel-Frequency Cepstral Coefficients) - Speech Recognition
    # ===================================================================
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    for i in range(13):
        features[f'mfcc_{i+1}_mean'] = float(np.mean(mfccs[i]))
        features[f'mfcc_{i+1}_std'] = float(np.std(mfccs[i]))
        features[f'mfcc_{i+1}_max'] = float(np.max(mfccs[i]))
        features[f'mfcc_{i+1}_min'] = float(np.min(mfccs[i]))

    # MFCC delta (velocity) and delta-delta (acceleration)
    mfcc_delta = librosa.feature.delta(mfccs)
    mfcc_delta2 = librosa.feature.delta(mfccs, order=2)

    features['mfcc_delta_mean'] = float(np.mean(mfcc_delta))
    features['mfcc_delta2_mean'] = float(np.mean(mfcc_delta2))

    # ===================================================================
    # 8. ENERGY & INTENSITY FEATURES
    # ===================================================================
    rms_energy = librosa.feature.rms(y=y)[0]
    features['rms_energy_mean'] = float(np.mean(rms_energy))
    features['rms_energy_std'] = float(np.std(rms_energy))
    features['rms_energy_max'] = float(np.max(rms_energy))
    features['rms_energy_min'] = float(np.min(rms_energy))

    # Energy variability (important for voice stability)
    features['energy_entropy'] = float(-np.sum(rms_energy * np.log2(rms_energy + 1e-10)))

    # ===================================================================
    # 9. VOICE BREAKS & PAUSES (Alzheimer's/Stroke indicator)
    # ===================================================================
    # Detect silent segments
    intervals = librosa.effects.split(y, top_db=20)
    if len(intervals) > 0:
        features['num_voice_breaks'] = len(intervals) - 1
        segment_durations = [(end - start) / sr for start, end in intervals]
        features['avg_segment_duration'] = float(np.mean(segment_durations))
        features['max_pause_duration'] = float(np.max(np.diff([end for _, end in intervals]) / sr)) if len(intervals) > 1 else 0.0
    else:
        features['num_voice_breaks'] = 0
        features['avg_segment_duration'] = 0.0
        features['max_pause_duration'] = 0.0

    # ===================================================================
    # 10. ZERO CROSSING RATE - Noisiness Indicator
    # ===================================================================
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    features['zcr_mean'] = float(np.mean(zcr))
    features['zcr_std'] = float(np.std(zcr))

    # ===================================================================
    # 11. CEPSTRAL PEAK PROMINENCE (CPP) - Voice Quality
    # ===================================================================
    # Higher CPP = better voice quality
    cepstrum = np.fft.ifft(np.log(np.abs(np.fft.fft(y)) + 1e-10)).real
    features['cpp'] = float(np.max(np.abs(cepstrum[:len(cepstrum)//2])))

    # ===================================================================
    # 12. DURATION FEATURES
    # ===================================================================
    features['total_duration'] = float(len(y) / sr)
    features['voiced_duration'] = float(len(f0_voiced) / sr) if len(f0_voiced) > 0 else 0.0
    features['voicing_ratio'] = float(features['voiced_duration'] / features['total_duration']) if features['total_duration'] > 0 else 0.0

    return features


def analyze_vowel_sequence(y, sr):
    """
    Analyze a sequence of different vowels (e.g., /a/-/e/-/i/-/o/-/u/)
    Useful for detecting articulation disorders and coordination issues
    """
    features = {}

    # Segment the audio into individual vowels (assuming 1-second segments)
    segment_length = int(sr * 1.0)  # 1 second per vowel
    num_segments = len(y) // segment_length

    if num_segments < 2:
        # If audio is too short, treat as single sustained vowel
        return extract_vowel_features(y, sr, vowel_type='sustained')

    # Extract features for each vowel segment
    segment_features = []
    for i in range(num_segments):
        start = i * segment_length
        end = start + segment_length
        segment = y[start:end]

        seg_features = extract_vowel_features(segment, sr, vowel_type='sustained')
        segment_features.append(seg_features)

    # Calculate transition metrics (coordination between vowels)
    f0_transitions = []
    formant_transitions = []

    for i in range(len(segment_features) - 1):
        current = segment_features[i]
        next_seg = segment_features[i + 1]

        f0_transitions.append(abs(current['f0_mean'] - next_seg['f0_mean']))
        formant_transitions.append(abs(current['f1'] - next_seg['f1']))

    # Aggregate features
    for key in segment_features[0].keys():
        values = [seg[key] for seg in segment_features]
        features[f'{key}_avg'] = float(np.mean(values))
        features[f'{key}_std'] = float(np.std(values))

    # Transition smoothness (important for MS, stroke)
    features['f0_transition_smoothness'] = float(np.mean(f0_transitions))
    features['formant_transition_smoothness'] = float(np.mean(formant_transitions))
    features['articulation_rate'] = float(num_segments / (len(y) / sr))

    return features


def classify_disease_from_features(features):
    """
    Rule-based classification helper (to be replaced with ML model)
    Provides initial disease likelihood scores based on clinical biomarkers
    """
    scores = {
        'parkinsons': 0,
        'alzheimers': 0,
        'als': 0,
        'multiple_sclerosis': 0,
        'stroke': 0,
        'healthy': 100
    }

    # Parkinson's indicators
    if features.get('f0_tremor_intensity', 0) > 50:
        scores['parkinsons'] += 30
    if features.get('jitter_relative', 0) > 1.0:
        scores['parkinsons'] += 20
    if features.get('shimmer_relative', 0) > 5.0:
        scores['parkinsons'] += 20
    if features.get('hnr', 20) < 15:
        scores['parkinsons'] += 15

    # Alzheimer's indicators (pauses, hesitations)
    if features.get('num_voice_breaks', 0) > 3:
        scores['alzheimers'] += 25
    if features.get('max_pause_duration', 0) > 2.0:
        scores['alzheimers'] += 20
    if features.get('energy_entropy', 0) > 5.0:
        scores['alzheimers'] += 20

    # ALS indicators (progressive muscle weakness)
    if features.get('rms_energy_mean', 1) < 0.01:
        scores['als'] += 30
    if features.get('shimmer_relative', 0) > 8.0:
        scores['als'] += 25
    if features.get('spectral_flux', 0) < 10:
        scores['als'] += 20

    # Multiple Sclerosis (coordination issues)
    if features.get('formant_transition_smoothness', 0) > 500:
        scores['multiple_sclerosis'] += 30
    if features.get('f0_transition_smoothness', 0) > 50:
        scores['multiple_sclerosis'] += 25

    # Stroke (articulation problems)
    if features.get('formant_dispersion', 0) < 500 or features.get('formant_dispersion', 0) > 2000:
        scores['stroke'] += 30
    if features.get('zcr_mean', 0) > 0.2:
        scores['stroke'] += 20

    # Calculate healthy score
    total_disease_score = sum([v for k, v in scores.items() if k != 'healthy'])
    scores['healthy'] = max(0, 100 - total_disease_score)

    # Normalize scores to percentages
    total = sum(scores.values())
    if total > 0:
        scores = {k: (v / total) * 100 for k, v in scores.items()}

    return scores


def generate_vowel_recording_instructions():
    """
    Return instructions for optimal vowel recording
    """
    return {
        'sustained_vowel': {
            'instructions': [
                'Choose ONE vowel sound: /a/ (as in "father"), /e/ (as in "see"), /i/ (as in "me"), /o/ (as in "go"), or /u/ (as in "you")',
                'Take a deep breath',
                'Say the vowel sound steadily for 5-10 seconds at comfortable pitch and loudness',
                'Try to maintain consistent volume throughout',
                'Avoid voice breaks or pauses'
            ],
            'optimal_duration': '5-10 seconds',
            'examples': ['Aaaaaaaaa', 'Eeeeeeeee', 'Iiiiiiiii', 'Ooooooooo', 'Uuuuuuuuu']
        },
        'vowel_sequence': {
            'instructions': [
                'Say all five vowels in sequence: /a/ - /e/ - /i/ - /o/ - /u/',
                'Hold each vowel for 1-2 seconds',
                'Brief pause between vowels',
                'Maintain consistent loudness',
                'Complete the full sequence'
            ],
            'optimal_duration': '10-15 seconds',
            'example': 'Aaa - Eee - Iii - Ooo - Uuu'
        }
    }
