# Manual Annotation Approach 🎯

## Overview
This folder contains the **"artisanal"** approach - high precision, manually annotated Qalqalah samples.

## Philosophy
- **Quality over Quantity**: 100-200 perfectly annotated samples
- **Precision**: Hand-marked exact Qalqalah timing boundaries  
- **Manual Control**: Visual waveform analysis for perfect timing

## Files in This Folder

### Core Tools
- **`qalqalah_annotator.py`** - GUI tool for manual annotation
- **`qalqalah_detection_model.py`** - Training script for small, precise dataset

### Dataset Management  
- **`qalqalah_samples/`** - Hand-annotated positive samples (organized by letter)
- **`negative_samples/`** - Carefully extracted negative samples
- **`extract_negative_samples.py`** - Script to extract quality negative samples
- **`balance_dataset.py`** - Balance positive:negative ratio

### Model Output
- **`qalqalah_model.pkl`** - Trained model from precise dataset

## How to Use This Approach

### 1. Manual Annotation (Recommended for Quality)
```bash
python qalqalah_annotator.py
```
- Open GUI tool
- Listen to audio segments  
- Mark precise Qalqalah boundaries
- Rate quality (1-5 stars)
- Save annotations

### 2. Extract Negative Samples
```bash
python extract_negative_samples.py
```
- Automatically extracts non-Qalqalah words
- Quality filtering (duration, clarity)
- Creates balanced dataset

### 3. Balance Dataset
```bash
python balance_dataset.py
```
- Ensures good positive:negative ratio
- Creates backup before changes
- Recommended ratio: 1:1 to 1:3

### 4. Train Model
```bash
python qalqalah_detection_model.py
```
- Loads all annotated samples
- Extracts audio features (MFCC, spectral)
- Trains SVM classifier
- Saves model as `qalqalah_model.pkl`

## Expected Results
- **Accuracy**: 95-98% on test set
- **Dataset Size**: 100-200 samples  
- **Time Investment**: 50-100 hours of annotation
- **Quality**: Research-grade precision

## When to Use This Approach
- ✅ Building research-quality model
- ✅ Need highest possible accuracy
- ✅ Have time for careful annotation
- ✅ Want to understand data deeply
- ❌ Need quick results
- ❌ Limited time for annotation
- ❌ Just want proof of concept

## Current Status
- **Positive Samples**: Check `qalqalah_samples/` for current count
- **Negative Samples**: Check `negative_samples/` for current count  
- **Model**: Trained model available in `qalqalah_model.pkl`

---
**Note**: This is the "slow but accurate" path. For rapid prototyping, see `../automated_mass_approach/` 