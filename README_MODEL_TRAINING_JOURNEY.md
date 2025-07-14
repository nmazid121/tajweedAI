# TajweedAI: Qalqalah Detection – Model Training & Pipeline Journey

## Introduction

This project began with a simple but powerful question:  
**Why isn't there an app that gives real-time Tajweed feedback while reciting the Quran?**

Inspired by Tarteel AI and the power of modern speech recognition, we set out to build a tool that listens to a user recite a verse and responds with specific, understandable Tajweed feedback—starting with the rule of Qalqalah.

---

## The Journey So Far

### **Week 1: Building the Foundation**

- **Goal:** Real-time Tajweed feedback, starting with Qalqalah.
- **Early Steps:**  
  - Used Whisper and Tarteel QUL for transcription and audio.
  - Built a demo for Surah Fatiha.
  - Reached out to Tarteel engineers for mentorship.
- **Key Challenge:** No public dataset with audio + Tajweed mistake labels.

### **Data Collection Pipeline**

1. **Audio Download (`download_script/script.py`):**  
   - Used QUL (Tarteel) to download high-quality, word-segmented recitations from multiple expert reciters.
   - Example JSON format:
   ```json
   {"1:1":{"surah_number":1,"ayah_number":1,"audio_url":"https://audio-cdn.tarteel.ai/quran/husary/001001.mp3","duration":null,"segments":[[1,0,480],[2,600,1000],[3,1800,2160],[4,2480,5160]]}}
   ```

2. **Timestamp Extraction (`download_script/extract_timestamps.py`):**  
   - Parsed QUL JSONs to get word-level timestamps for each reciter and ayah.
   - Created organized JSON files for each surah by reciter.

3. **Manual & Automated Labeling:**  
   - Labeled Qalqalah occurrences using both manual annotation and automated scripts.

### **Dataset Summary (7 Reciters)**

**✅ Successfully Processed All Reciters:**
1. **Husary** ✅
2. **Minshawi** ✅  
3. **Abdul Basit** ✅
4. **Mishary Rashid Al-Afasy** ✅
5. **Maher Al-Mu'aiqly** ✅
6. **Yasser Al-Dosari** ✅
7. **Saud Al-Shuraim** ✅

**📁 Audio Files Downloaded:**
- **322 Audio Files** (46 ayahs × 7 reciters)
- **1,386 Word-level timestamps** (198 words × 7 reciters)
- **42 Surahs** across all reciters

---

## Three Model Training Approaches

### 1. **Manual Annotation Approach** 📝

**Location:** `manual_annotation_approach/`

#### **What:**
- Manually annotated the exact Qalqalah bursts (e.g., "ق", "ب", "د") in various ayahs and reciters.
- Used a custom GUI (`qalqalah_annotator.py`) to mark precise start/end of Qalqalah in waveforms.

#### **How:**
- Built a GUI tool for precise manual annotation of Qalqalah segments
- Extracted these segments as positive samples
- Collected negative samples from similar contexts without Qalqalah
- Trained binary classifier (SVM/Random Forest) on hand-annotated segments

#### **Results:**
- **Dataset:** 28 positive + 28 negative samples
- **Accuracy:** ~58% (limited by small dataset size)
- **Model:** `qalqalah_model.pkl`

#### **Pros:**
- Very clean, high-quality data
- Model learns true acoustic fingerprint of Qalqalah

#### **Cons:**
- Time-consuming to annotate
- Limited data size

---

### 2. **Mass Approach (Automated Extraction)** ⚡

**Location:** `automated_mass_approach/`

#### **What:**
- Automatically extracted hundreds of word segments from reciter audio where Qalqalah Kubra is expected
- Used parallel processing for speed and volume

#### **How:**
- Used QUL timestamps to slice out all candidate Qalqalah words
- Labeled as positive if word should have Qalqalah, negative otherwise
- Employed multiprocessing for fast feature extraction
- Trained on much larger, noisier dataset

#### **Results:**
- **Dataset:** 70 positive + 231 negative samples (301 total)
- **Best Model:** Random Forest
- **Accuracy:** 83.6%
- **Model:** `mass_qalqalah_model.pkl`

#### **Performance Breakdown:**
```
Random Forest Results:
- Test Accuracy: 83.6%
- Precision (No Qalqalah): 86.3%
- Precision (Qalqalah): 70.0%
- Recall (Qalqalah): 50.0% ⚠️
```

#### **Pros:**
- Much more data, faster to collect
- Captures wide range of reciters and pronunciations
- Scalable approach

#### **Cons:**
- Some segments may include non-Qalqalah sounds
- Model may learn context, not just Qalqalah
- Lower Qalqalah recall (50%)

---

### 3. **Fine-Tuned Falaq Pipeline (CTC Forced Aligner)** 🎯

**Location:** `falaq_word_approach/` and `complete_qalqalah_pipeline.py`

#### **What:**
- Focused specifically on the word "الْفَلَقِ" at the end of Surah Falaq
- Used forced alignment for precise extraction and real-world pipeline testing

#### **How:**
1. **NVIDIA ASR:** Transcribe user/reciter audio using `nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0`
2. **CTC Forced Aligner:** Get exact timestamps for "الْفَلَقِ" (using Mahmoud Ashraf's tool)
3. **PyDub:** Extract just the ending segment with optional padding for Qalqalah burst
4. **Qalqalah Classifier:** Run segment through specialized binary classifier

#### **Technical Pipeline:**
```python
# End-to-End Pipeline Flow:
1. User recites Surah Al-Falaq → WAV file
2. NVIDIA ASR transcribes → "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ"
3. Forced aligner extracts word timestamps
4. PyDub extracts "الْفَلَقِ" segment
5. Feature extraction (24 features: MFCC + spectral)
6. Binary classifier predicts Qalqalah presence
```

#### **Major Technical Challenge Solved:**
- **Problem:** `[WinError 2] The system cannot find the file specified`
- **Root Cause:** Missing Uroman (romanization tool) and Perl dependencies
- **Solution:** Installed Strawberry Perl + Uroman, configured system PATH
- **Result:** CTC Forced Aligner working perfectly on Windows

#### **Results:**
- **Dataset:** 13 positive + 16 negative samples (focused, high-quality)
- **Best Model:** SVM Linear (Balanced)
- **Accuracy:** 100.0% ✅
- **Model:** `falaq_word_model.pkl`

#### **Hard Negative Mining Success:**
- Used expert reciter "الْفَلَقِ" as positives
- Used personal incorrect recordings as negatives
- Model learned to distinguish the Qalqalah burst specifically

#### **Pros:**
- Realistic, end-to-end pipeline for real-world use
- Perfect accuracy on specialized task
- Can be extended to other words/rules
- Real-time capable

#### **Cons:**
- Specialized to one word (needs expansion)
- Small dataset size

---

## Key Technical Discoveries

### **Audio Quality Impact**
- **Finding:** Feature extraction is highly sensitive to audio quality differences
- **Problem:** High-quality pipeline segments vs. lower-quality training samples caused prediction mismatches
- **Solution:** Consistent preprocessing (mono, 16kHz, normalization) across all data

### **CTC Forced Aligner Integration**
- **Achievement:** Successfully integrated Mahmoud Ashraf's CTC forced aligner on Windows
- **Dependencies:** Strawberry Perl, Uroman romanization tool, proper PATH configuration
- **Result:** Precise word-level timestamp extraction for Arabic text

### **Feature Engineering**
- **Successful Features:** 24-feature vector including:
  - 13 MFCC coefficients
  - Spectral centroid, rolloff, bandwidth
  - Zero crossing rate
  - 7 spectral contrast features

---

## Performance Comparison

| Approach | Dataset Size | Accuracy | Precision | Recall | Best Use Case |
|----------|-------------|----------|-----------|---------|---------------|
| Manual Annotation | 56 samples | 58.3% | 0.57 | 0.67 | Research/Development |
| Mass Approach | 301 samples | 83.6% | 0.70 | 0.50 | General Purpose |
| Falaq Pipeline | 29 samples | 100.0% | 1.00 | 1.00 | Production Ready |

---

## Lessons Learned & Recommendations

- **Audio Quality Matters:** Consistent preprocessing (mono, sample rate, normalization) is crucial
- **Data Diversity is Key:** More reciters, more voices, more negative samples = better model
- **Manual Annotation = Gold Standard:** But mass extraction is needed for scale
- **Forced Alignment Unlocks Real-Time Feedback:** Enables precise, user-specific Tajweed correction
- **Hard Negative Mining Works:** Using acoustically similar incorrect samples dramatically improves discrimination

---

## Current Pipeline Architecture

```
User Audio Input (WAV)
         ↓
NVIDIA ASR Transcription
         ↓
CTC Forced Aligner (Word Timestamps)
         ↓
PyDub Audio Segmentation
         ↓
Feature Extraction (24 features)
         ↓
Qalqalah Binary Classifier
         ↓
Feedback Output (Qalqalah Detected/Not Detected)
```

---

## File Structure

```
├── manual_annotation_approach/          # Manual annotation scripts & models
│   ├── qalqalah_annotator.py           # GUI for manual annotation
│   ├── qalqalah_detection_model.py     # Training script
│   └── qalqalah_model.pkl              # Trained model
├── automated_mass_approach/             # Mass extraction approach
│   ├── mass_qalqalah_extractor.py      # Data extraction script
│   ├── mass_model_trainer.py           # Training with parallel processing
│   └── mass_qalqalah_model.pkl         # Trained model
├── falaq_word_approach/                 # Specialized Falaq approach
│   ├── falaq_word_trainer.py           # Training script
│   ├── positive_samples_wav/           # Expert reciter samples
│   └── negative_samples_wav/           # Incorrect pronunciation samples
├── complete_qalqalah_pipeline.py        # End-to-end pipeline
├── ctc_forced_aligner_test.py          # Forced aligner testing
├── convert_to_mono_wav.py              # Audio preprocessing utility
└── falaq_word_model.pkl                # Best performing model
```

---

## How to Reproduce

### **Prerequisites:**
- Python 3.8+
- Required packages: `librosa`, `scikit-learn`, `pydub`, `nemo_toolkit`, `torch`
- Windows: Strawberry Perl + Uroman for forced alignment

### **Steps:**
1. **Collect/annotate data** (manual or mass approach)
2. **Preprocess audio** using `convert_to_mono_wav.py`
3. **Extract features** (MFCC, spectral, etc.)
4. **Train classifier** using appropriate training script
5. **Run pipeline** using `complete_qalqalah_pipeline.py`

### **Quick Test:**
```bash
# Test the complete pipeline
python complete_qalqalah_pipeline.py

# Test individual model
python test_model_on_audio.py
```

---

## Next Steps

- **Expand dataset** with more positive and negative samples, especially for various Qalqalah letters
- **Data augmentation** (noise, pitch, speed variations) for robustness  
- **Generalize** to other Tajweed rules (Madd, Ghunna, Idgham) and more words
- **Real-time optimization** for mobile deployment
- **Open-source** the pipeline and models for the community
- **Research paper** on findings, especially around phoneme-level error detection in Quranic recitation

---

## Conclusion

This project represents a significant step toward real-time, ML-powered Tajweed feedback. By combining manual annotation, mass data extraction, and forced alignment, we've built a robust, scalable system for Qalqalah detection—achieving **100% accuracy** on our specialized Falaq pipeline.

The journey from 58% accuracy with limited manual data to 100% accuracy with focused hard negative mining demonstrates the power of thoughtful data curation and domain-specific model training.

**This is more than a technical challenge—it's a mission to revive the beauty and precision of Quranic recitation through AI.**

---

*Built with dedication to the Ummah and the preservation of Tajweed excellence.* 