# TajweedAI: Detecting Qalqalah in Quranic Recitation

### *Building with dedication to the Ummah and the preservation of Tajweed excellence.*

### Short Demo Run of the Classifier on a Single Ayah

[![Watch the demo on Streamable](https://cdn.streamable.com/image/btk5af.jpg)](https://streamable.com/btk5af)


## Introduction

This project began with a simple but powerful question:
**Why isn't there an app that gives real-time Tajweed feedback while reciting the Quran?**

Inspired by Tarteel AI and the power of modern speech recognition, we set out to build a tool that listens to a user recite a verse and responds with specific, understandable Tajweed feedback—starting with the rule of Qalqalah.

## Project Overview
This project aims to build an AI system that detects Qalqalah Kubra (major Qalqalah) in Quranic recitation. The system leverages forced alignment, audio processing, and machine learning to provide targeted feedback on the correct pronunciation of Tajweed rules, with an initial focus on the letter Qaf (ق).

## Tech Stack
- **Python 3.11**
- **Libraries:**
  - `librosa`, `numpy`, `soundfile`, `pydub`, `joblib`
  - `scikit-learn` (for model training)
  - `nemo_toolkit`, `torch` (for ASR)
  - `ffmpeg` (audio conversion)
- **Tools:**
  - **CTC Forced Aligner** (for precise phoneme/word alignment)
- **Data:**
  - Quran metadata (JSON)
  - Audio from multiple expert reciters (WAV, MP3)

---

## Methodology: A Three-Pronged Approach

To tackle the challenge of having no public dataset with audio and Tajweed mistake labels, we pursued three distinct model training strategies, each with its own trade-offs.

### 1. Manual Annotation Approach 
**Location:** `manual_annotation_approach/`

- **Concept:** Manually annotate the exact acoustic bursts of Qalqalah sounds (e.g., "ق", "ب", "د") using a custom GUI to create a small, high-quality dataset.
- **Process:**
  1. Built a GUI tool (`qalqalah_annotator.py`) for precise manual annotation.
  2. Extracted these segments as positive samples.
  3. Collected negative samples from similar contexts without Qalqalah.
  4. Trained a binary classifier (SVM/Random Forest) on the hand-annotated segments.
- **Results:** ~58% accuracy, limited by the extremely small dataset (56 samples).
- **Pros:** Very clean, high-quality data that teaches the model the true acoustic fingerprint of Qalqalah.
- **Cons:** Incredibly time-consuming to annotate and not scalable.

### 2. Mass Approach (Automated Extraction) 
**Location:** `automated_mass_approach/`

- **Concept:** Automatically extract hundreds of word segments from reciter audio where Qalqalah Kubra is *expected* to occur, creating a large but potentially noisy dataset.
- **Process:**
  1. Used word-level timestamps from Tarteel's QUL dataset to slice out all candidate words.
  2. Labeled segments as positive if the word should have Qalqalah, negative otherwise.
  3. Employed Python's multiprocessing for fast feature extraction across 7 reciters.
  4. Trained a model on this much larger dataset.
- **Results:** 83.6% accuracy on a dataset of 301 samples, but with a low recall (50%) for detecting actual Qalqalah.
- **Pros:** Much more data, faster to collect, and captures a wide range of reciter pronunciations.
- **Cons:** Segments may include non-Qalqalah sounds, leading the model to learn context rather than just the target sound.

### 3. Fine-Tuned Falaq Pipeline (CTC Forced Aligner) 
**Location:** `falaq_word_approach/` and `complete_qalqalah_pipeline.py`

- **Concept:** Focus on a single, high-value word ("الْفَلَقِ") and use a forced aligner to precisely extract *only* the target sound, then use "hard negative mining" with our own incorrect pronunciations to train a highly specialized model.
- **Process:**
  1. **NVIDIA ASR:** Transcribe user/reciter audio.
  2. **CTC Forced Aligner:** Get exact timestamps for the target word.
  3. **PyDub:** Extract just the word segment.
  4. **Qalqalah Classifier:** Run the segment through a specialized binary classifier.
- **Results:** **100% accuracy** on the internal validation set, **57.14% accuracy** on an external test set.
- **Pros:** Realistic, end-to-end pipeline for real-world use; demonstrates the potential of the method with perfect internal accuracy.
- **Cons:** Specialized to one word; the gap between internal and external accuracy shows it has not yet generalized.

---

## 🔬 Key Technical Discoveries & Solutions

- **Audio Quality Sensitivity:** Feature extraction is highly sensitive to audio quality. Consistent preprocessing (mono, 16kHz, normalization) across all data was critical to prevent prediction mismatches.
- **CTC Forced Aligner Integration:** Successfully integrated a powerful CTC forced aligner on Windows by solving complex dependencies involving Strawberry Perl and the Uroman romanization tool, enabling precise word-level extraction.
- **Hard Negative Mining:** Using acoustically similar but incorrect pronunciations (our own) as negative samples dramatically improved the model's ability to discriminate the subtle Qalqalah burst.
- **Feature Engineering:** A 24-feature vector (13 MFCCs, spectral features, zero-crossing rate, and 7 spectral contrast features) proved effective for classification.

---

## Performance & Results

The three approaches yielded vastly different results, highlighting the trade-off between data quantity and quality.

| Approach | Dataset Size | Accuracy | Precision | Recall | Best Use Case |
|:---|:---:|:---:|:---:|:---:|:---|
| Manual Annotation | 56 samples | 58.3% | 0.57 | 0.67 | Research / Prototyping |
| Mass Approach | 301 samples | 83.6% | 0.70 | 0.50 | General Purpose Model |
| **Falaq Pipeline** | **29 samples** | **100% / 57.14%** | **1.00** | **1.00** | **Proof-of-Concept** |

*Note: The Falaq Pipeline achieved 100% on its internal validation set but 57.14% (4/7 correct) on an external test set of real-world examples.*

**Key Insight:** The model is currently biased toward "Not Qalqalah" when faced with unseen data. The 57.14% external accuracy score makes it clear that while the forced alignment *method* is highly effective for creating clean training data, the model needs a much more diverse and balanced dataset to generalize to new reciters and environments.

---

## Final Pipeline Architecture

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

## Project Directory

```
├── manual_annotation_approach/       # Manual annotation scripts & models
│   ├── qalqalah_annotator.py         # GUI for manual annotation
│   └── qalqalah_model.pkl            # Trained model
├── automated_mass_approach/          # Mass extraction approach
│   ├── mass_qalqalah_extractor.py    # Data extraction script
│   └── mass_qalqalah_model.pkl       # Trained model
├── falaq_word_approach/              # Specialized Falaq approach
│   ├── falaq_word_trainer.py         # Training script
│   ├── positive_samples_wav/         # Expert reciter samples
│   └── negative_samples_wav/         # Incorrect pronunciation samples
├── complete_qalqalah_pipeline.py     # End-to-end pipeline for testing
├── ctc_forced_aligner_test.py        # Forced aligner testing script
├── convert_to_mono_wav.py            # Audio preprocessing utility
└── README.md                         # This file
```

---

## How to Reproduce

### Prerequisites
- Python 3.8+
- Required packages: `librosa`, `scikit-learn`, `pydub`, `nemo_toolkit`, `torch`
- Windows: **Strawberry Perl** and **Uroman** configured in system PATH for the forced aligner.

### Steps
1. **Prepare Data:** Collect or annotate audio samples for your target rule.
2. **Preprocess Audio:** Ensure all audio is in a consistent format (e.g., mono, 16kHz WAV) using scripts like `convert_to_mono_wav.py`.
3. **Extract Features:** Use the feature extraction logic found in the training scripts.
4. **Train Classifier:** Run the appropriate training script (`falaq_word_trainer.py` is recommended).
5. **Run Pipeline:** Test the full flow with `complete_qalqalah_pipeline.py`.

---

## Next Steps

- **Expand Dataset:** This is the highest priority. Add more Qalqalah and non-Qalqalah examples from diverse reciters to address the generalization gap.
- **Data Augmentation:** Introduce noise, pitch, and speed variations to improve model robustness.
- **Generalize the Pipeline:** Adapt the successful "Falaq Pipeline" to other Tajweed rules like Madd, Ghunna, and Idgham.
- **Automate Evaluation:** Build a larger, labeled external test set to create a more reliable benchmark for future improvements.
- **Publish Findings:** Write a research paper on the methodology and findings, particularly around phoneme-level error detection in Quranic recitation.

---

## Conclusion

This project represents a significant step toward real-time, ML-powered Tajweed feedback. The journey from 58% accuracy with limited manual data to **100% accuracy on a specialized internal set** proves the effectiveness of the forced alignment and hard negative mining pipeline.

However, the **57.14% accuracy on an external test set** serves as a crucial benchmark, demonstrating that while the *method* for data curation is sound, the current model has not yet generalized. This work lays a strong and promising foundation, with a clear path forward focused on dataset expansion and diversification.

This is more than a technical challenge—it's a mission to revive the beauty and precision of Quranic recitation through the responsible use of AI.

---

**Project by:** Nabhan Mazid and Muaz Ahmed

**Contact:** [nabhanmazid@gmail.com](mailto:nabhanmazid@gmail.com) | **GitHub:** [nmazid121](https://github.com/nmazid121) | **LinkedIn:** [Nabhan Mazid](https://linkedin.com/in/nabhan-mazid)
