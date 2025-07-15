# Qalqalah Detection Pipeline

A complete pipeline for detecting and classifying Qalqalah pronunciation in Quranic recitation, specifically focusing on the word "الْفَلَقِ" from Surah Al-Falaq.

## 🎯 Overview

This pipeline combines:
1. **ASR (Automatic Speech Recognition)** - Transcribes Arabic audio
2. **Forced Alignment** - Precisely locates the target word in audio
3. **Audio Extraction** - Extracts the target word segment
4. **Classification** - Determines if Qalqalah is pronounced correctly

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Run the setup script
python setup_pipeline.py

# Or install manually
pip install -r requirements.txt
```

### 2. Verify Model File

Make sure you have the trained classifier model:
```
falaq_word_model.pkl
```

### 3. Run the Pipeline

```bash
python complete_qalqalah_pipeline.py
```

## 🔧 Fixed Issues

### Problem: Stable-ts Alignment Error
**Issue**: The original pipeline used `stable-ts` with `--text` parameter, which is not supported.

**Solution**: Implemented a multi-tier approach:
- **Primary**: WhisperX for accurate forced alignment
- **Fallback**: ASR + approximate word detection

### Key Improvements:
1. **Robust Alignment**: Uses WhisperX when available, falls back gracefully
2. **Better Error Handling**: Clear error messages and fallback options
3. **Flexible Dependencies**: Works with or without optional packages

## 📁 File Structure

```
├── complete_qalqalah_pipeline.py  # Main pipeline
├── setup_pipeline.py              # Setup script
├── requirements.txt               # Dependencies
├── falaq_word_model.pkl          # Trained classifier (required)
└── wav_audio_correct/            # Test audio files
    ├── nabhan_correct_qalqalah.wav
    ├── nabhan_incorrect_qalqalah.wav
    └── Ayah_001.wav
```

## 🎵 Supported Audio Formats

- WAV (recommended)
- MP3
- M4A
- FLAC

## 🔍 Pipeline Steps

### Step 1: ASR Transcription
- Uses NVIDIA NeMo ASR model
- Transcribes full Arabic audio to text
- Supports Arabic language recognition

### Step 2: Forced Alignment
**Option A (Recommended)**: WhisperX
- Precise word-level timestamps
- High accuracy for Arabic text
- Requires: `pip install whisperx`

**Option B (Fallback)**: Approximate Detection
- Estimates word position based on audio duration
- Works without additional dependencies
- Less accurate but functional

### Step 3: Audio Extraction
- Extracts the target word "الْفَلَقِ"
- Converts to mono, 16kHz for consistency
- Saves as `extracted_falaq.wav`

### Step 4: Classification
- Uses trained ML model (24 features)
- Features: MFCC, spectral features, contrast
- Output: Correct/Incorrect Qalqalah + confidence

## 🛠️ Configuration

### Target Text
The pipeline is configured for Surah Al-Falaq:
```python
target_text = "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ"
target_word = "الْفَلَقِ"
```

### Model Features
The classifier uses 24 audio features:
- MFCC coefficients (13)
- Spectral centroid (1)
- Spectral rolloff (1)
- Zero crossing rate (1)
- Spectral bandwidth (1)
- Spectral contrast (7)

## 📊 Output Format

```python
{
    'transcription': 'قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ',
    'timestamps': (start_time, end_time),
    'extracted_file': 'extracted_falaq.wav',
    'classification': {
        'prediction': 1,  # 1=correct, 0=incorrect
        'confidence': 0.85,
        'probabilities': [0.15, 0.85],
        'result_text': '✅ CORRECT Qalqalah'
    }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **NeMo Installation Error**
   ```bash
   pip install nemo_toolkit[asr] --extra-index-url https://pypi.ngc.nvidia.com
   ```

2. **WhisperX Not Available**
   - Pipeline will automatically use fallback method
   - Install with: `pip install whisperx`

3. **Model File Missing**
   - Ensure `falaq_word_model.pkl` is in the same directory
   - This file contains the trained classifier

4. **Audio File Issues**
   - Convert to WAV format if needed
   - Ensure audio is clear and contains the target ayah

### Performance Tips

1. **For Better Accuracy**: Install WhisperX
2. **For Faster Processing**: Use shorter audio clips
3. **For GPU Acceleration**: Install CUDA versions of PyTorch

## 🔬 Testing

The pipeline includes test files:
- `nabhan_correct_qalqalah.wav` - Correct Qalqalah
- `nabhan_incorrect_qalqalah.wav` - Incorrect Qalqalah
- `Ayah_001.wav` - General test file

## 📈 Future Improvements

1. **Multi-word Support**: Extend to other Qalqalah words
2. **Real-time Processing**: Stream audio for live feedback
3. **Web Interface**: Create user-friendly web app
4. **Model Fine-tuning**: Improve classification accuracy

## 🤝 Contributing

To contribute:
1. Test with different audio files
2. Improve alignment accuracy
3. Add support for more Tajweed rules
4. Optimize performance

## 📄 License

This project is part of the Tajweed AI initiative for Quranic recitation feedback. 