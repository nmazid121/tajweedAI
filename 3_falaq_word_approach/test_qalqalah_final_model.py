import os
import joblib
import librosa
import numpy as np
from pydub import AudioSegment

def ensure_mono_wav(audio_file):
    if not audio_file.lower().endswith('.wav'):
        return None
    try:
        audio = AudioSegment.from_wav(audio_file)
        if audio.channels == 1:
            return audio_file
        mono_audio = audio.set_channels(1)
        tmp_path = audio_file[:-4] + '_mono.wav'
        mono_audio.export(tmp_path, format='wav')
        return tmp_path
    except Exception as e:
        print(f"❌ Error loading {audio_file}: {e}")
        return None

def extract_features_from_audio(audio_file):
    try:
        audio_data, sample_rate = librosa.load(audio_file, sr=22050, mono=True)
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        spectral_centroid_mean = np.mean(spectral_centroid)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
        spectral_rolloff_mean = np.mean(spectral_rolloff)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        zero_crossing_rate_mean = np.mean(zero_crossing_rate)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
        spectral_bandwidth_mean = np.mean(spectral_bandwidth)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        spectral_contrast_mean = np.mean(spectral_contrast, axis=1)
        features = np.concatenate([
            mfccs_mean,
            [spectral_centroid_mean],
            [spectral_rolloff_mean],
            [zero_crossing_rate_mean],
            [spectral_bandwidth_mean],
            spectral_contrast_mean
        ])
        return features
    except Exception as e:
        print(f"❌ Error processing {audio_file}: {e}")
        return None

def main():
    model_path = '3_falaq_word_approach/qalqalah_final_model.pkl'
    test_dir = 'wav_audio_correct'
    model = joblib.load(model_path)
    test_files = [f for f in os.listdir(test_dir) if f.lower().endswith('.wav')]
    print(f"Testing {len(test_files)} files in {test_dir}...")
    results = []
    for fname in test_files:
        fpath = os.path.join(test_dir, fname)
        mono_path = ensure_mono_wav(fpath)
        if mono_path is None:
            print(f"Skipping {fname} (not a wav or unreadable)")
            continue
        features = extract_features_from_audio(mono_path)
        if features is None:
            print(f"Skipping {fname} (feature extraction failed)")
            continue
        pred = model.predict([features])[0]
        label = 'Qalqalah' if pred == 1 else 'Not Qalqalah'
        print(f"{fname}: {label}")
        results.append((fname, label))
        if mono_path != fpath and os.path.exists(mono_path):
            os.remove(mono_path)
    # Optionally, let user enter ground truth for accuracy
    if results:
        print("\nIf you want to calculate accuracy, enter the ground truth for each file:")
        correct = 0
        total = 0
        for fname, label in results:
            gt = input(f"{fname} (model: {label}) - Enter ground truth (1=Qalqalah, 0=Not Qalqalah, Enter to skip): ")
            if gt.strip() == '':
                continue
            total += 1
            if (gt == '1' and label == 'Qalqalah') or (gt == '0' and label == 'Not Qalqalah'):
                correct += 1
        if total > 0:
            print(f"\nModel accuracy on your labeled test set: {correct}/{total} = {correct/total:.2%}")
        else:
            print("No ground truth entered, skipping accuracy calculation.")

if __name__ == "__main__":
    main() 