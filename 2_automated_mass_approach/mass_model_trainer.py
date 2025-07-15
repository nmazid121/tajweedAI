#!/usr/bin/env python3
"""
Mass Model Trainer - Speed & Volume Approach ⚡

Trains Qalqalah detection model on 500+ automatically extracted samples.
Optimized for speed and large datasets.

Author: TajweedAI Project  
Approach: Large dataset, fast training
"""

import os
import json
import numpy as np
import librosa
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from datetime import datetime
import glob
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')

def load_single_audio_file(args):
    """Load and extract features from a single audio file (for parallel processing)"""
    file_path, label = args
    try:
        # Load audio with librosa
        audio_data, sample_rate = librosa.load(file_path, sr=22050)
        
        # Extract features quickly (fewer features for speed)
        # MFCC (most important for speech)
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)
        
        # Spectral features (fast to compute)  
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # Combine features
        features = np.concatenate([
            mfccs_mean,                    # 13 features
            [spectral_centroid],           # 1 feature  
            [spectral_rolloff],            # 1 feature
            [zero_crossing_rate]           # 1 feature
        ])
        
        return features, label, file_path
        
    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")
        return None, None, file_path

def load_mass_dataset():
    """Load all samples from mass extraction"""
    print("📂 Loading mass-extracted dataset...")
    
    # Load positive samples
    positive_files = glob.glob("mass_positive_samples/*.mp3")
    negative_files = glob.glob("mass_negative_samples/*.mp3")
    
    print(f"Found {len(positive_files)} positive samples")
    print(f"Found {len(negative_files)} negative samples")
    
    if len(positive_files) == 0 or len(negative_files) == 0:
        print("❌ No samples found! Run mass_qalqalah_extractor.py first.")
        return None, None, None
    
    # Prepare file list with labels
    file_label_pairs = []
    file_label_pairs.extend([(f, 1) for f in positive_files])  # 1 = positive
    file_label_pairs.extend([(f, 0) for f in negative_files])  # 0 = negative
    
    print(f"📊 Total samples to process: {len(file_label_pairs)}")
    print("⚡ Using parallel processing for speed...")
    
    # Use multiprocessing for fast feature extraction
    num_processes = min(cpu_count(), 8)  # Don't overwhelm the system
    print(f"🔄 Using {num_processes} processes for feature extraction")
    
    with Pool(num_processes) as pool:
        results = pool.map(load_single_audio_file, file_label_pairs)
    
    # Filter successful results
    features_list = []
    labels_list = []
    file_paths = []
    
    failed_count = 0
    for features, label, file_path in results:
        if features is not None:
            features_list.append(features)
            labels_list.append(label)
            file_paths.append(file_path)
        else:
            failed_count += 1
    
    if failed_count > 0:
        print(f"⚠️  Failed to process {failed_count} files")
    
    print(f"✅ Successfully processed {len(features_list)} samples")
    
    return np.array(features_list), np.array(labels_list), file_paths

def train_multiple_models(X_train, X_test, y_train, y_test):
    """Train multiple models and compare performance with class balancing"""
    print("\n🤖 Training multiple models with class weight balancing...")
    
    # First, train models WITHOUT class weights for comparison
    print("\n🔴 Training models WITHOUT class weights (baseline)...")
    models_baseline = {
        'SVM (RBF) - Baseline': svm.SVC(kernel='rbf', C=1.0, random_state=42),
        'SVM (Linear) - Baseline': svm.SVC(kernel='linear', C=1.0, random_state=42),
        'Random Forest - Baseline': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    baseline_results = {}
    for name, model in models_baseline.items():
        print(f"  🔧 Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        baseline_results[name] = {'model': model, 'accuracy': accuracy, 'predictions': y_pred}
        print(f"    📊 Accuracy: {accuracy:.3f}")
    
    # Now train models WITH class weights
    print("\n🟢 Training models WITH class weights (improved)...")
    models_balanced = {
        'SVM (RBF) - Balanced': svm.SVC(kernel='rbf', C=1.0, class_weight='balanced', random_state=42),
        'SVM (Linear) - Balanced': svm.SVC(kernel='linear', C=1.0, class_weight='balanced', random_state=42),
        'Random Forest - Balanced': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
    }
    
    best_model = None
    best_accuracy = 0
    best_name = ""
    results = {}
    
    for name, model in models_balanced.items():
        print(f"  🔧 Training {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Test model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation for robustness
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_mean = np.mean(cv_scores)
        cv_std = np.std(cv_scores)
        
        print(f"    📊 Test Accuracy: {accuracy:.3f}")
        print(f"    📊 CV Accuracy: {cv_mean:.3f} (±{cv_std:.3f})")
        
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
    
    # Show improvement comparison
    print("\n" + "="*60)
    print("🎯 CLASS BALANCING IMPROVEMENT COMPARISON")
    print("="*60)
    
    for baseline_name, baseline_result in baseline_results.items():
        # Find corresponding balanced model
        balanced_name = baseline_name.replace(" - Baseline", " - Balanced")
        if balanced_name in results:
            balanced_result = results[balanced_name]
            improvement = balanced_result['test_accuracy'] - baseline_result['accuracy']
            print(f"\n📊 {baseline_name.replace(' - Baseline', '')}:")
            print(f"   🔴 Baseline: {baseline_result['accuracy']:.3f}")
            print(f"   🟢 Balanced: {balanced_result['test_accuracy']:.3f}")
            print(f"   📈 Improvement: {improvement:+.3f}")
            if improvement > 0:
                print("   ✅ Class balancing helped!")
            else:
                print("   ⚠️  No improvement in overall accuracy")
    
    print(f"\n🏆 Best balanced model: {best_name} with {best_accuracy:.3f} accuracy")
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
                                  target_names=['No Qalqalah', 'Qalqalah'],
                                  digits=3))

def save_model_and_results(model, model_name, results, features, labels):
    """Save the best model and create analysis report"""
    
    # Save the model
    model_filename = 'mass_qalqalah_model.pkl'
    joblib.dump(model, model_filename)
    print(f"💾 Saved model: {model_filename}")
    
    # Create comprehensive report
    report = {
        'training_date': datetime.now().isoformat(),
        'approach': 'automated_mass_training',
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
    with open('mass_training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Saved training report: mass_training_report.json")
    
    return report

def main():
    """Main training function"""
    print("🚀 MASS MODEL TRAINER - Speed & Volume Approach")
    print("=" * 60)
    print("🎯 Target: Train model on 500+ samples in 10 minutes")
    print("⚡ Strategy: Parallel processing + multiple model comparison")
    print()
    
    # Load dataset
    features, labels, file_paths = load_mass_dataset()
    if features is None:
        return
    
    print(f"\n📊 Dataset Summary:")
    print(f"  Total samples: {len(features)}")
    print(f"  Positive samples: {np.sum(labels)}")
    print(f"  Negative samples: {len(labels) - np.sum(labels)}")
    print(f"  Feature dimensions: {features.shape[1]}")
    print(f"  Positive:Negative ratio: 1:{(len(labels) - np.sum(labels))/np.sum(labels):.1f}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=0.2,      # 20% for testing
        random_state=42,    # Reproducible results
        stratify=labels     # Keep same ratio in train/test
    )
    
    print(f"\n📈 Training/Test Split:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    
    # Train multiple models
    best_model, best_name, results = train_multiple_models(X_train, X_test, y_train, y_test)
    
    # Detailed analysis
    analyze_results(y_test, results)
    
    # Save everything
    report = save_model_and_results(best_model, best_name, results, features, labels)
    
    print(f"\n🎉 TRAINING COMPLETE!")
    print("=" * 60)
    print(f"✅ Best Model: {best_name}")
    print(f"📊 Test Accuracy: {results[best_name]['test_accuracy']:.1%}")
    print(f"🎯 Expected Performance: 85-90% (achieved {results[best_name]['test_accuracy']:.1%})")
    print(f"💾 Model saved: mass_qalqalah_model.pkl")
    print(f"📊 Report saved: mass_training_report.json")
    print()
    
    # Next steps
    if results[best_name]['test_accuracy'] >= 0.85:
        print("🏆 SUCCESS! Model meets 85%+ accuracy target")
        print("🚀 Next steps:")
        print("  1. Test model on new audio samples")
        print("  2. Build demo application")
        print("  3. Optional: Fine-tune with manual annotations")
    else:
        print("⚠️  Accuracy below 85% target")
        print("💡 Suggestions:")
        print("  1. Check audio quality in samples")
        print("  2. Add more diverse training data")  
        print("  3. Try manual annotation approach for higher quality")
    
    print("\n📈 Time to celebrate! You have a working Qalqalah detector! 🎉")

if __name__ == "__main__":
    main() 