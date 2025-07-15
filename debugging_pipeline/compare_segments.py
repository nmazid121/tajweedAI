import os
import numpy as np
import librosa
import joblib

def extract_features_from_audio(audio_file):
    y, sr = librosa.load(audio_file, sr=22050)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs, axis=1)
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr), axis=1)
    features = np.concatenate([
        mfccs_mean,                    # 13 features
        [spectral_centroid],           # 1 feature
        [spectral_rolloff],            # 1 feature
        [zero_crossing_rate],          # 1 feature
        [spectral_bandwidth],          # 1 feature
        spectral_contrast              # 7 features
    ])
    return features

def main():
    # Paths to the two files
    pipeline_segment = os.path.abspath("trial_1/segment_3_الفلق.wav")
    mishary_sample = os.path.abspath("falaq_word_approach/positive_samples_wav/mishary_falaq.wav")
    model_path = os.path.abspath("falaq_word_model.pkl")

    print(f"Pipeline segment: {pipeline_segment}")
    print(f"Mishary positive sample: {mishary_sample}")

    # Extract features
    features_pipeline = extract_features_from_audio(pipeline_segment)
    features_mishary = extract_features_from_audio(mishary_sample)

    print("\nFeature vector (pipeline segment):\n", features_pipeline)
    print("\nFeature vector (Mishary sample):\n", features_mishary)
    print("\nDifference (abs):\n", np.abs(features_pipeline - features_mishary))
    print(f"\nMean absolute difference: {np.mean(np.abs(features_pipeline - features_mishary))}")

    # Load model
    model = joblib.load(model_path)
    pred_pipeline = model.predict(features_pipeline.reshape(1, -1))[0]
    pred_mishary = model.predict(features_mishary.reshape(1, -1))[0]
    print(f"\nClassifier prediction (pipeline segment): {pred_pipeline}")
    print(f"Classifier prediction (Mishary sample): {pred_mishary}")

    if pred_pipeline == pred_mishary:
        print("\n✅ Predictions match.")
    else:
        print("\n❌ Predictions differ!")

if __name__ == "__main__":
    main() 