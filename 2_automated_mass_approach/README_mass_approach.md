# Automated Mass Approach ⚡

## Overview  
This folder contains the **"speed & volume"** approach - automatically generate 500+ samples in 30 minutes.

## Philosophy  
- **Quantity over Precision**: 500-1000+ samples for robust training
- **Speed**: Automated extraction from existing timestamps  
- **Engineering Focus**: Get working model ASAP, iterate later
- **Good Enough**: 85-90% accuracy in days, not months

## Files in This Folder

### Core Scripts
- **`mass_qalqalah_extractor.py`** - Main script to auto-extract all samples
- **`mass_model_trainer.py`** - Training script for large, noisy dataset
- **`arabic_text_mapper.py`** - Maps timestamps to Arabic text for detection

### Generated Datasets
- **`mass_positive_samples/`** - All words ending in ق ط ب ج د
- **`mass_negative_samples/`** - All other words  
- **`dataset_analysis.json`** - Statistics and quality metrics

### Model Output
- **`mass_qalqalah_model.pkl`** - Trained model from large dataset

## How to Use This Approach

### 1. Extract Massive Dataset (30 minutes)
```bash
python mass_qalqalah_extractor.py
```
- Processes all 1,386 timestamped words
- Auto-detects Qalqalah words (ending in ق ط ب ج د)  
- Clips audio for each word
- Creates balanced positive/negative samples

### 2. Train Model (10 minutes)
```bash
python mass_model_trainer.py
```
- Loads 500+ audio samples
- Extracts features in parallel
- Trains on large, noisy dataset
- Saves model as `mass_qalqalah_model.pkl`

### 3. Analyze Results
```bash
python analyze_mass_dataset.py
```
- Dataset statistics and quality metrics
- Accuracy breakdown by reciter
- Identifies problematic samples

## Expected Results
- **Accuracy**: 85-90% on test set
- **Dataset Size**: 500-1000+ samples
- **Time Investment**: 2-3 hours total
- **Quality**: Good enough for proof of concept

## Strategy: The Hybrid Approach

### Phase 1: Speed (This Week) ⚡
1. **Run mass extraction** → Get 500+ samples in 30 minutes
2. **Train baseline model** → 85-90% accuracy by Friday  
3. **Ship working demo** → Proof of concept complete

### Phase 2: Polish (Next Week) 🎯  
1. **Use `../manual_annotation_approach/`** for 100 golden samples
2. **Fine-tune baseline model** → 95%+ accuracy
3. **Portfolio-ready project** → Research-grade results

## When to Use This Approach
- ✅ Need working model THIS WEEK
- ✅ Want proof of concept quickly
- ✅ Building for internship applications  
- ✅ Have limited annotation time
- ✅ Want to test feasibility first
- ❌ Need research-grade precision immediately
- ❌ Have months for careful annotation

## Data Sources Used
- **7 Reciters**: Husary, Minshawi, Abdul Basit, Mishary, Maher, Yasser, Shuraim
- **6 Surahs**: Al-Fatiha, Al-Lahab, Al-Ikhlas, Al-Falaq, Al-Kafirun, Al-Infitar  
- **1,386 Words**: With precise start/end timestamps
- **Source**: `../download_script/extracted_timestamps/`

## Current Status
- **Setup**: Ready for mass extraction
- **Scripts**: Need to be created and run
- **Target**: 500+ samples by end of today

---
**Note**: This is the "fast but noisy" path. For research-grade precision, see `../manual_annotation_approach/` 