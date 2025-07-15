#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FALAQ WORD SPECIALIZED MODEL TRAINER

Trains a specialized binary classifier to detect correct vs incorrect Qalqalah
in the word الْفَلَقِ (Al-falaq) only.

Dataset: 13 positive + 17 negative samples
Target: 90%+ accuracy for الْفَلَقِ Qalqalah detection
"""

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
import warnings
warnings.filterwarnings('ignore')

def extract_features_from_audio(audio_file):
    """Extract audio features from a single audio file"""
    try:
        # Load the audio file
        audio_data, sample_rate = librosa.load(audio_file, sr=22050)
        
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
        
        # Feature 6: Spectral Contrast (good for detecting bursts)
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

def load_falaq_dataset():
    """Load the specialized Falaq dataset"""
    print("�� Loading Falaq Word Dataset...")
    
    # Load positive samples
    positive_files = glob.glob("falaq_word_approach/positive_samples_wav/*.wav")
    negative_files = glob.glob("falaq_word_approach/negative_samples_wav/*.wav")
    
    print(f"Found {len(positive_files)} positive samples")
    print(f"Found {len(negative_files)} negative samples")
    
    if len(positive_files) == 0 or len(negative_files) == 0:
        print("❌ No samples found! Check your falaq_word_approach folder.")
        return None, None, None
    
    # Prepare file list with labels
    file_label_pairs = []
    file_label_pairs.extend([(f, 1) for f in positive_files])  # 1 = correct Qalqalah
    file_label_pairs.extend([(f, 0) for f in negative_files])  # 0 = incorrect Qalqalah
    
    print(f"📊 Total samples to process: {len(file_label_pairs)}")
    
    # Extract features
    features_list = []
    labels_list = []
    file_paths = []
    
    failed_count = 0
    for audio_file, label in file_label_pairs:
        print(f"Processing {os.path.basename(audio_file)}...")
        
        features = extract_features_from_audio(audio_file)
        if features is not None:
            features_list.append(features)
            labels_list.append(label)
            file_paths.append(audio_file)
        else:
            failed_count += 1
    
    if failed_count > 0:
        print(f"⚠️  Failed to process {failed_count} files")
    
    print(f"✅ Successfully processed {len(features_list)} samples")
    
    return np.array(features_list), np.array(labels_list), file_paths

def train_specialized_models(X_train, X_test, y_train, y_test):
    """Train multiple specialized models and compare performance"""
    print("\n🤖 Training specialized Falaq Qalqalah detection models...")
    
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
        print(f"\n�� Training {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Test model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation for robustness
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
        
        # Track best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
    
    print(f"\n🏆 Best model: {best_name} with {best_accuracy:.3f} accuracy")
    return best_model, best_name, results

def analyze_results(y_test, results):
    """Detailed analysis of model performance"""
    print("\n📊 DETAILED PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    for name, result in results.items():
        print(f"\n📈 {name}:")
        print(f"  Test Accuracy: {result['test_accuracy']:.3f}")
        print(f"  CV Score: {result['cv_mean']:.3f} ± {result['cv_std']:.3f}")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, result['predictions'])
        print(f"  Confusion Matrix:")
        print(f"    TN: {cm[0,0]}, FP: {cm[0,1]}")  
        print(f"    FN: {cm[1,0]}, TP: {cm[1,1]}")
        
        # Classification report
        print(f"  Classification Report:")
        print(classification_report(y_test, result['predictions'], 
                                  target_names=['Incorrect Qalqalah', 'Correct Qalqalah'],
                                  digits=3))

def save_model_and_results(model, model_name, results, features, labels):
    """Save the best model and create analysis report"""
    
    # Save the model
    model_filename = 'falaq_word_model.pkl'
    joblib.dump(model, model_filename)
    print(f"💾 Saved specialized model: {model_filename}")
    
    # Create comprehensive report
    report = {
        'training_date': datetime.now().isoformat(),
        'approach': 'specialized_falaq_word_detection',
        'dataset_size': len(features),
        'positive_samples': int(np.sum(labels)),
        'negative_samples': int(len(labels) - np.sum(labels)),
        'feature_count': features.shape[1],
        'best_model': model_name,
        'model_results': {}
    }
    
    # Add all model results
    for name, result in results.items():
        report['model_results'][name] = {
            'test_accuracy': float(result['test_accuracy']),
            'cv_mean': float(result['cv_mean']),
            'cv_std': float(result['cv_std'])
        }
    
    # Save report
    with open('falaq_training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Saved training report: falaq_training_report.json")
    
    return report

def main():
    """Main training function"""
    print("�� FALAQ WORD SPECIALIZED MODEL TRAINER")
    print("=" * 60)
    print("🎯 Target: Detect correct vs incorrect Qalqalah in الْفَلَقِ")
    print("📊 Dataset: 13 positive + 17 negative samples")
    print("🎯 Goal: 90%+ accuracy for specialized detection")
    print()
    
    # Load dataset
    features, labels, file_paths = load_falaq_dataset()
    if features is None:
        return
    
    print(f"\n📊 Dataset Summary:")
    print(f"  Total samples: {len(features)}")
    print(f"  Positive samples (Correct Qalqalah): {np.sum(labels)}")
    print(f"  Negative samples (Incorrect Qalqalah): {len(labels) - np.sum(labels)}")
    print(f"  Feature dimensions: {features.shape[1]}")
    print(f"  Positive:Negative ratio: 1:{(len(labels) - np.sum(labels))/np.sum(labels):.1f}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=0.3,      # 30% for testing (small dataset)
        random_state=42,    # Reproducible results
        stratify=labels     # Keep same ratio in train/test
    )
    
    print(f"\n📈 Training/Test Split:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    
    # Train specialized models
    best_model, best_name, results = train_specialized_models(X_train, X_test, y_train, y_test)
    
    # Detailed analysis
    analyze_results(y_test, results)
    
    # Save everything
    report = save_model_and_results(best_model, best_name, results, features, labels)
    
    print(f"\n🎉 TRAINING COMPLETE!")
    print("=" * 60)
    print(f"✅ Best Model: {best_name}")
    print(f"📊 Test Accuracy: {results[best_name]['test_accuracy']:.1%}")
    print(f"🎯 Expected Performance: 90%+ (achieved {results[best_name]['test_accuracy']:.1%})")
    print(f"�� Model saved: falaq_word_model.pkl")
    print(f"�� Report saved: falaq_training_report.json")
    print()
    
    # Next steps
    if results[best_name]['test_accuracy'] >= 0.90:
        print("🏆 SUCCESS! Model meets 90%+ accuracy target")
        print("🚀 Next steps:")
        print("  1. Test model on your nabhan audio files")
        print("  2. Build demo application")
        print("  3. Deploy for real-time detection")
    else:
        print("⚠️  Accuracy below 90% target")
        print("💡 Suggestions:")
        print("  1. Add more diverse training samples")
        print("  2. Try different feature extraction methods")
        print("  3. Fine-tune model parameters")
    
    print("\n📈 Time to test your specialized الْفَلَقِ detector! 🎉")

if __name__ == "__main__":
    main()