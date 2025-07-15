from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import librosa
import numpy as np
import json
import os
import glob


def load_audio_data():
    # Load all the positive and negative audio data + annotations

    # Lists will store the data
    audio_files = []
    labels = []
    metadata = []

    print("Loading positive samples (Qalqalah):")
    positive_folders = ['ق', 'ب', 'د']
    for letter in positive_folders:
        letter_path = f"qalqalah_samples/{letter}"
        if os.path.exists(letter_path):
            # Go through each reciter
            for reciter in os.listdir(letter_path):
                reciter_path = os.path.join(letter_path, reciter)
                if os.path.isdir(reciter_path):
                    # Go through each ayah
                    for ayah in os.listdir(reciter_path):
                        ayah_path = os.path.join(reciter_path, ayah)
                        if os.path.isdir(ayah_path):
                            # Find the MP3 file
                            mp3_files = [f for f in os.listdir(ayah_path) if f.endswith('.mp3')]
                            if mp3_files:
                                audio_file = os.path.join(ayah_path, mp3_files[0])
                                audio_files.append(audio_file)
                                labels.append(1)  # 1 = positive (has Qalqalah)
                                metadata.append({
                                    'letter': letter,
                                    'reciter': reciter,
                                    'ayah': ayah,
                                    'type': 'positive'
                                })
                                print(f"  Found: {letter}/{reciter}/{ayah}")

    print("Loading negative samples (Non-Qalqalah):")
    negative_path = "negative_samples"
    if os.path.exists(negative_path):
        # Go through each reciter
        for reciter in os.listdir(negative_path):
            reciter_path = os.path.join(negative_path, reciter)
            if os.path.isdir(reciter_path):
                # Find all MP3 files in this reciter's folder
                mp3_files = [f for f in os.listdir(reciter_path) if f.endswith('.mp3')]
                for mp3_file in mp3_files:
                    audio_file = os.path.join(reciter_path, mp3_file)
                    audio_files.append(audio_file)
                    labels.append(0)  # 0 = negative (no Qalqalah)
                    metadata.append({
                        'reciter': reciter,
                        'filename': mp3_file,
                        'type': 'negative'
                    })
                    print(f"  Found: {reciter}/{mp3_file}")

    print(f"\nTotal samples loaded: {len(audio_files)}")
    print(f"Positive samples: {sum(labels)}")
    print(f"Negative samples: {len(labels) - sum(labels)}")
    
    return audio_files, labels, metadata


def extract_features(audio_file):
    """Extract audio features from a single audio file"""
    try:
        # Load the audio file
        # sr=22050 means 22,050 samples per second (standard for speech)
        audio_data, sample_rate = librosa.load(audio_file, sr=22050)
        
        # Feature 1: MFCC (13 coefficients)
        # This captures the spectral shape - most important for speech recognition
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)  # Take average across time
        
        # Feature 2: Spectral Centroid
        # Where is the "center of mass" of the spectrum?
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        spectral_centroid_mean = np.mean(spectral_centroid)
        
        # Feature 3: Spectral Rolloff
        # Below this frequency lies 85% of the energy
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
        spectral_rolloff_mean = np.mean(spectral_rolloff)
        
        # Feature 4: Zero Crossing Rate
        # How often does the signal cross zero?
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        zero_crossing_rate_mean = np.mean(zero_crossing_rate)
        
        # Feature 5: Spectral Bandwidth
        # How "spread out" is the spectrum?
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
        
        return features  # Total: 17 features
        
    except Exception as e:
        print(f"Error processing {audio_file}: {e}")
        return None


def extract_all_features(audio_files):
    """Extract features from all audio files"""
    print("Extracting features from all audio files...")
    
    all_features = []
    failed_files = []
    
    for i, audio_file in enumerate(audio_files):
        print(f"Processing {i+1}/{len(audio_files)}: {os.path.basename(audio_file)}")
        
        features = extract_features(audio_file)
        if features is not None:
            all_features.append(features)
        else:
            failed_files.append(audio_file)
            # Add a placeholder to keep indices aligned
            all_features.append(np.zeros(17))  # 17 zeros as placeholder
    
    if failed_files:
        print(f"Warning: Failed to process {len(failed_files)} files")
    
    return np.array(all_features)


def train_model(features, labels):
    """Train the Qalqalah detection model with class weight comparison"""
    print("\n=== TRAINING THE MODEL ===")
    
    # Split data into training and testing sets
    # 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, 
        test_size=0.2,      # 20% for testing
        random_state=42,    # For reproducible results
        stratify=labels     # Keep same ratio of positive/negative in both sets
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Testing set: {len(X_test)} samples")
    print(f"Training positive samples: {sum(y_train)}")
    print(f"Training negative samples: {len(y_train) - sum(y_train)}")
    
    # Train two models for comparison
    print("\n--- Training Standard SVM (without class weights) ---")
    model_standard = svm.SVC(
        kernel='rbf',
        C=1.0,
        random_state=42
    )
    model_standard.fit(X_train, y_train)
    y_pred_standard = model_standard.predict(X_test)
    
    print("\n--- Training Balanced SVM (with class weights) ---")
    model_balanced = svm.SVC(
        kernel='rbf',
        C=1.0,
        class_weight='balanced',  # 🎯 MAGIC LINE: Penalizes mistakes on rare class more heavily
        random_state=42
    )
    model_balanced.fit(X_train, y_train)
    y_pred_balanced = model_balanced.predict(X_test)
    
    # Compare performance
    print("\n" + "="*60)
    print("🎯 PERFORMANCE COMPARISON")
    print("="*60)
    
    # Standard model results
    accuracy_standard = accuracy_score(y_test, y_pred_standard)
    print(f"\n🔴 Standard SVM (no class weights):")
    print(f"   Overall Accuracy: {accuracy_standard:.2%}")
    print("   Detailed Report:")
    print(classification_report(y_test, y_pred_standard, 
                              target_names=['No Qalqalah', 'Qalqalah']))
    
    # Balanced model results
    accuracy_balanced = accuracy_score(y_test, y_pred_balanced)
    print(f"\n🟢 Balanced SVM (with class weights):")
    print(f"   Overall Accuracy: {accuracy_balanced:.2%}")
    print("   Detailed Report:")
    print(classification_report(y_test, y_pred_balanced, 
                              target_names=['No Qalqalah', 'Qalqalah']))
    
    # Improvement summary
    print(f"\n🎯 IMPROVEMENT SUMMARY:")
    print(f"   Accuracy change: {accuracy_balanced - accuracy_standard:+.2%}")
    if accuracy_balanced > accuracy_standard:
        print("   ✅ Class balancing improved overall performance!")
    else:
        print("   ⚠️  Class balancing didn't improve overall accuracy, but likely improved Qalqalah recall")
    
    # Use the balanced model as the final model
    model = model_balanced
    y_pred = y_pred_balanced
    
    # Show some predictions
    print("\nSample Predictions (Balanced Model):")
    for i in range(min(5, len(X_test))):
        actual = "Qalqalah" if y_test[i] == 1 else "No Qalqalah"
        predicted = "Qalqalah" if y_pred[i] == 1 else "No Qalqalah"
        confidence = "✓" if y_test[i] == y_pred[i] else "✗"
        print(f"  {confidence} Actual: {actual}, Predicted: {predicted}")
    
    return model, X_test, y_test, y_pred


def main():
    """Main function to run the complete pipeline"""
    print("🎯 QALQALAH DETECTION MODEL TRAINING")
    print("=" * 50)
    
    # Step 1: Load all audio files
    audio_files, labels, metadata = load_audio_data()
    
    if len(audio_files) == 0:
        print("No audio files found! Make sure your sample folders exist.")
        return
    
    # Step 2: Extract features from all files
    features = extract_all_features(audio_files)
    
    # Step 3: Train and evaluate the model
    model, X_test, y_test, y_pred = train_model(features, labels)
    
    # Step 4: Save the model for later use
    import joblib
    joblib.dump(model, 'qalqalah_model.pkl')
    print("\n✅ Model saved as 'qalqalah_model.pkl'")
    
    print("\n🎉 Training Complete!")
    print("You can now use this model to detect Qalqalah in new audio!")


if __name__ == "__main__":
    main()