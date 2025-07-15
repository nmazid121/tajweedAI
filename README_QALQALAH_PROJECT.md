# Qalqalah AI Project: Detecting Qaf (ق) Qalqalah in Quranic Recitation

## 🚀 Project Overview
This project aims to build an AI system that detects Qalqalah Kubra (major Qalqalah) for the letter Qaf (ق) at the end of ayahs in Quranic recitation. The system leverages forced alignment, audio processing, and machine learning to provide feedback on the correct pronunciation of Qalqalah.

---

## 🛤️ Project Journey & Milestones

### 1. **Initial Exploration**
- **Goal:** Detect Qalqalah Kubra (ق) at the end of ayahs.
- **First Steps:**
  - Extracted ayahs ending with Qaf from Quran metadata.
  - Gathered audio from multiple reciters.

### 2. **Timestamp Extraction**
- **Expanded Scope:**
  - Extracted timestamps for Surah Al-Falaq and Al-Inshiqaq from various reciters.
  - Filtered and organized these timestamps and audio segments.

### 3. **Audio Segmentation**
- **Last Word Extraction:**
  - Developed scripts to extract the last word segment from each ayah for all reciters.
  - Organized segments for use with a CTC forced aligner.

### 4. **Precise Qaf ('aq') Extraction**
- **Forced Alignment:**
  - Used CTC forced aligner to extract just the "aq" sound of Qaf with a small window before/after.
  - Handled mono WAV conversion and filename parsing issues.

### 5. **Dataset Organization**
- **Positive/Negative Samples:**
  - Organized final positive and negative samples into dedicated folders.
  - Ensured all files were in mono WAV format (44.1kHz, 16-bit PCM).

### 6. **Model Training & Testing**
- **Training:**
  - Trained a machine learning model on the final samples.
  - Used MFCCs and spectral features for classification.
- **Testing:**
  - Created a test script to evaluate the model on a folder of real-world examples (`wav_audio_correct`).
  - Achieved 100% internal validation, 57.14% accuracy on external test set.

### 7. **Analysis & Documentation**
- **Comprehensive Analysis:**
  - Summarized findings, challenges, and next steps in a detailed analysis document.
  - Created this README as a final project summary.

---

## 🗂️ File & Directory Structure

```
TAJWEED AI/
├── 1_manual_annotation_approach/
│   ├── balance_dataset.py
│   ├── extract_negative_samples.py
│   ├── qalqalah_annotator.py
│   ├── qalqalah_detection_model.py
│   └── ...
├── 2_automated_mass_approach/
│   ├── mass_model_trainer.py
│   ├── mass_qalqalah_extractor.py
│   └── ...
├── 3_falaq_word_approach/
│   ├── falaq_word_trainer.py
│   ├── test_qalqalah_final_model.py
│   └── ...
├── download_script/
│   ├── extract_timestamps.py
│   └── ...
├── wav_audio_correct/           # Final test set (all mono WAV)
├── extracted_aq_segments/       # Output of forced aligner 'aq' extraction
├── convert_test_files_to_wav.py # Utility for audio format conversion
├── extract_aq_segments_from_qaf_ayahs.py # Main forced aligner extraction script
├── QALQALAH_PROJECT_ANALYSIS.md # Final analysis & findings
├── README_QALQALAH_PROJECT.md   # This file
└── ...
```

---

## 🛠️ Tech Stack
- **Python 3.11**
- **Libraries:**
  - `librosa`, `numpy`, `soundfile`, `pydub`, `joblib`
  - `scikit-learn` (for model training)
  - `ffmpeg` (audio conversion)
- **Tools:**
  - **CTC Forced Aligner** (for precise phoneme/word alignment)
- **Data:**
  - Quran metadata (JSON)
  - Audio from multiple reciters (WAV, MP3)

---

## 🧠 Methodology
1. **Data Preparation:**
   - Extract ayahs ending with Qaf from metadata.
   - Gather and standardize audio from multiple reciters.
2. **Forced Alignment:**
   - Use CTC forced aligner to get precise timestamps for the "aq" sound.
   - Extract segments with a small window for context.
3. **Feature Extraction:**
   - Compute MFCCs, spectral centroid, rolloff, bandwidth, contrast, and zero-crossing rate.
4. **Model Training:**
   - Train a classifier (e.g., SVM, RandomForest) on positive/negative samples.
5. **Testing & Evaluation:**
   - Test on a separate, real-world set (`wav_audio_correct`).
   - Manual ground truth labeling for accuracy calculation.
6. **Analysis:**
   - Review false positives/negatives, bias, and model limitations.

---

## 📊 Results & Findings
- **Internal Validation:** 100% accuracy
- **External Test Set:** 57.14% accuracy (4/7 correct)
- **Key Insights:**
  - Model is currently biased toward "Not Qalqalah"
  - Needs more diverse and balanced training data
  - Forced aligner is effective for precise segment extraction

---

## 📝 Lessons Learned
- **Audio Format Consistency is Critical:**
  - All files must be mono, 44.1kHz, 16-bit PCM for reliable processing.
- **Forced Alignment is Powerful:**
  - Enables extraction of precise phoneme/word segments for targeted training.
- **Data Diversity Matters:**
  - More reciters and varied pronunciations improve model generalization.
- **Manual Labeling is Essential:**
  - Human-in-the-loop is needed for ground truth and error analysis.

---

## 🏁 Final Thoughts & Next Steps
- **Expand Dataset:** Add more Qalqalah and non-Qalqalah examples from diverse reciters.
- **Improve Model:** Experiment with new features, model types, and hyperparameters.
- **Refine Forced Alignment:** Fine-tune segment extraction and validate outputs.
- **Automate Evaluation:** Build a larger, labeled test set and automate accuracy reporting.

This project demonstrates a full pipeline for phoneme-level Tajweed feedback using modern AI and forced alignment. With further data and tuning, it can become a robust tool for Quranic recitation education.

---

**Project by:** [Your Name/Team]

**Contact:** [Your Email/Contact Info] 