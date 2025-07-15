#!/usr/bin/env python3
"""
Quick Qalqalah Detection Test on Real Audio Files - FALAQ Model Only

Tests our trained Falaq model on 3 WAV files in wav_audio_correct folder.
"""

import os
import numpy as np
import librosa
import joblib
import warnings
warnings.filterwarnings('ignore')

def extract_features_from_audio(audio_file):
    """Extract features from a single audio file (same as training)"""
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
        
        # Combine all features into one array
        features = np.concatenate([
            mfccs_mean,                    # 13 features
            [spectral_centroid_mean],      # 1 feature
            [spectral_rolloff_mean],       # 1 feature
            [zero_crossing_rate_mean],     # 1 feature
            [spectral_bandwidth_mean]      # 1 feature
        ])
        
        return features
        
    except Exception as e:
        print(f"❌ Error processing {audio_file}: {e}")
        return None

def test_audio_file(model, audio_file, expected_result=None):
    """Test a single audio file and return prediction"""
    print(f"\n🎵 Testing: {os.path.basename(audio_file)}")
    print("-" * 50)
    
    # Extract features
    features = extract_features_from_audio(audio_file)
    if features is None:
        return None
    
    # Get prediction
    prediction = model.predict([features])[0]
    prediction_proba = model.predict_proba([features])[0] if hasattr(model, 'predict_proba') else None
    
    # Display results
    result_text = "QALQALAH DETECTED" if prediction == 1 else "No Qalqalah"
    confidence = prediction_proba[prediction] if prediction_proba is not None else "N/A"
    
    print(f"📊 Prediction: {result_text}")
    if prediction_proba is not None:
        print(f"📊 Confidence: {confidence:.2%}")
        print(f"📊 Probabilities: No Qalqalah: {prediction_proba[0]:.2%}, Qalqalah: {prediction_proba[1]:.2%}")
    
    if expected_result is not None:
        expected_text = "QALQALAH" if expected_result == 1 else "No Qalqalah"
        is_correct = prediction == expected_result
        status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        print(f"🎯 Expected: {expected_text}")
        print(f"🎯 Result: {status}")
    
    return prediction, prediction_proba

def main():
    """Main testing function"""
    print("�� QALQALAH DETECTION - Falaq MODEL TEST")
    print("=" * 60)
    
    # Try to load the Falaq model specifically
    model_path = 'falaq_word_model.pkl'
    
    model = None
    model_name = ""
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            model_name = model_path
            print(f"✅ Loaded Falaq model: {model_path}")
        except Exception as e:
            print(f"❌ Failed to load {model_path}: {e}")
    else:
        print(f"❌ Falaq model not found at: {model_path}")
        print("💡 Please run the automated Falaq trainer first to create this model.")
    
    if model is None:
        print("❌ No Falaq model found! Please train the Falaq model first.")
        return
    
    # Test files with expected results
    test_files = [
        ('wav_audio_correct/nabhan_correct_qalqalah.wav', 1, "Should have proper Qalqalah"),
        ('wav_audio_correct/nabhan_incorrect_qalqalah.wav', 0, "Should have incorrect/poor Qalqalah - model should detect issues"),
        ('wav_audio_correct/Ayah_001.wav', None, "General test - unknown expected result")
    ]
    
    results = []
    
    for audio_file, expected_result, description in test_files:
        if not os.path.exists(audio_file):
            print(f"❌ File not found: {audio_file}")
            continue
            
        print(f"\n📝 Description: {description}")
        result = test_audio_file(model, audio_file, expected_result)
        if result is not None:
            results.append((audio_file, result[0], result[1], expected_result))
    
    # Summary
    print("\n" + "="*60)
    print("�� TESTING SUMMARY")
    print("="*60)
    
    correct_predictions = 0
    total_tests = 0
    
    for audio_file, prediction, proba, expected in results:
        filename = os.path.basename(audio_file)
        pred_text = "Qalqalah" if prediction == 1 else "No Qalqalah"
        confidence = proba[prediction] if proba is not None else "N/A"
        
        print(f"\n🎵 {filename}:")
        print(f"   Prediction: {pred_text}")
        print(f"   Confidence: {confidence}")
        
        if expected is not None:
            expected_text = "Qalqalah" if expected == 1 else "No Qalqalah"
            is_correct = prediction == expected
            status = "✅" if is_correct else "❌"
            print(f"   Expected: {expected_text} {status}")
            if is_correct:
                correct_predictions += 1
            total_tests += 1
    
    if total_tests > 0:
        accuracy = correct_predictions / total_tests
        print(f"\n🎯 Overall Accuracy: {accuracy:.1%} ({correct_predictions}/{total_tests})")
    
    print(f"\n🎉 Testing complete! Model: {model_name}")

if __name__ == "__main__":
    main()