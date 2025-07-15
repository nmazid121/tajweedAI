import os
import numpy as np
import librosa
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import glob
import joblib
import json
from datetime import datetime
from pydub import AudioSegment
import warnings
warnings.filterwarnings('ignore')

def ensure_mono_wav(audio_file):
    """Ensure the audio file is mono WAV. If not, convert and return new path."""
    if not audio_file.lower().endswith('.wav'):
        return None  # Only process wav files
    try:
        audio = AudioSegment.from_wav(audio_file)
        if audio.channels == 1:
            return audio_file
        # Convert to mono
        mono_audio = audio.set_channels(1)
        tmp_path = audio_file[:-4] + '_mono.wav'
        mono_audio.export(tmp_path, format='wav')
        return tmp_path
    except Exception as e:
        print(f"❌ Error loading {audio_file}: {e}")
        return None

def extract_features_from_audio(audio_file):
    """Extract audio features from a single audio file"""
    try:
        # Load the audio file
        audio_data, sample_rate = librosa.load(audio_file, sr=22050, mono=True)
        # Feature 1: MFCC (13 coefficients)
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)
        # Feature 2: Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        spectral_centroid_mean = np.mean(spectral_centroid)
        # Feature 3: Spectral Rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
        spectral_rolloff_mean = np.mean(spectral_rolloff)
        # Feature 4: Zero Crossing Rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        zero_crossing_rate_mean = np.mean(zero_crossing_rate)
        # Feature 5: Spectral Bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
        spectral_bandwidth_mean = np.mean(spectral_bandwidth)
        # Feature 6: Spectral Contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        spectral_contrast_mean = np.mean(spectral_contrast, axis=1)
        # Combine all features into one array
        features = np.concatenate([
            mfccs_mean,                    # 13 features
            [spectral_centroid_mean],      # 1 feature
            [spectral_rolloff_mean],       # 1 feature
            [zero_crossing_rate_mean],     # 1 feature
            [spectral_bandwidth_mean],     # 1 feature
            spectral_contrast_mean         # 7 features
        ])
        return features
    except Exception as e:
        print(f"❌ Error processing {audio_file}: {e}")
        return None

def load_qalqalah_final_dataset():
    print("\n🔎 Loading Qalqalah Final Dataset...")
    pos_dir = "3_falaq_word_approach/final_pos_samples_mp3"
    neg_dir = "3_falaq_word_approach/final_neg_samples_mp3"
    positive_files = glob.glob(os.path.join(pos_dir, "*.wav"))
    negative_files = glob.glob(os.path.join(neg_dir, "*.wav"))
    print(f"Found {len(positive_files)} positive samples")
    print(f"Found {len(negative_files)} negative samples")
    if len(positive_files) == 0 or len(negative_files) == 0:
        print("❌ No samples found! Check your final sample folders.")
        return None, None, None
    file_label_pairs = []
    file_label_pairs.extend([(f, 1) for f in positive_files])
    file_label_pairs.extend([(f, 0) for f in negative_files])
    print(f"📊 Total samples to process: {len(file_label_pairs)}")
    features_list = []
    labels_list = []
    file_paths = []
    failed_count = 0
    for audio_file, label in file_label_pairs:
        mono_path = ensure_mono_wav(audio_file)
        if mono_path is None:
            print(f"⚠️  Skipping non-wav or unreadable file: {audio_file}")
            failed_count += 1
            continue
        features = extract_features_from_audio(mono_path)
        if features is not None:
            features_list.append(features)
            labels_list.append(label)
            file_paths.append(audio_file)
        else:
            failed_count += 1
        # Clean up temp mono file if created
        if mono_path != audio_file and os.path.exists(mono_path):
            os.remove(mono_path)
    if failed_count > 0:
        print(f"⚠️  Failed to process {failed_count} files")
    print(f"✅ Successfully processed {len(features_list)} samples")
    return np.array(features_list), np.array(labels_list), file_paths

def train_and_save_final_model():
    print("\n🤖 QALQALAH FINAL MODEL TRAINER")
    print("=" * 60)
    features, labels, file_paths = load_qalqalah_final_dataset()
    if features is None:
        return
    print(f"\n📊 Dataset Summary:")
    print(f"  Total samples: {len(features)}")
    print(f"  Positive samples: {np.sum(labels)}")
    print(f"  Negative samples: {len(labels) - np.sum(labels)}")
    print(f"  Feature dimensions: {features.shape[1]}")
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=0.3,
        random_state=42,
        stratify=labels
    )
    print(f"\n📈 Training/Test Split:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    # Train models
    models = {
        'SVM (RBF) - Balanced': svm.SVC(kernel='rbf', C=1.0, class_weight='balanced', random_state=42),
        'SVM (Linear) - Balanced': svm.SVC(kernel='linear', C=1.0, class_weight='balanced', random_state=42),
        'Random Forest - Balanced': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
    }
    best_model = None
    best_accuracy = 0
    best_name = ""
    results = {}
    for name, model in models.items():
        print(f"\n🚀 Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_mean = np.mean(cv_scores)
        cv_std = np.std(cv_scores)
        print(f"  📊 Test Accuracy: {accuracy:.3f}")
        print(f"  📊 CV Accuracy: {cv_mean:.3f} (±{cv_std:.3f})")
        results[name] = {
            'model': model,
            'test_accuracy': accuracy,
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'predictions': y_pred
        }
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
    print(f"\n🏆 Best model: {best_name} with {best_accuracy:.3f} accuracy")
    # Save model
    model_filename = 'qalqalah_final_model.pkl'
    joblib.dump(best_model, model_filename)
    print(f"💾 Saved final model: {model_filename}")
    # Save report
    report = {
        'training_date': datetime.now().isoformat(),
        'approach': 'qalqalah_final_detection',
        'dataset_size': len(features),
        'positive_samples': int(np.sum(labels)),
        'negative_samples': int(len(labels) - np.sum(labels)),
        'feature_count': features.shape[1],
        'best_model': best_name,
        'model_results': {}
    }
    for name, result in results.items():
        report['model_results'][name] = {
            'test_accuracy': float(result['test_accuracy']),
            'cv_mean': float(result['cv_mean']),
            'cv_std': float(result['cv_std'])
        }
    with open('qalqalah_final_training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"📊 Saved training report: qalqalah_final_training_report.json")
    print(f"\n🎉 FINAL TRAINING COMPLETE!")
    print("=" * 60)
    print(f"✅ Best Model: {best_name}")
    print(f"📊 Test Accuracy: {results[best_name]['test_accuracy']:.1%}")
    print(f"💾 Model saved: {model_filename}")
    print(f"📊 Report saved: qalqalah_final_training_report.json")

def main():
    train_and_save_final_model()

if __name__ == "__main__":
    main() 