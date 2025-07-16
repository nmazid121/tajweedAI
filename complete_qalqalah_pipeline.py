#!/usr/bin/env python3
"""
Robust Qalqalah Detection Pipeline
Handles NumPy compatibility issues and provides fallback options
"""

import os
import numpy as np
import librosa
import joblib
import warnings
from pydub import AudioSegment
import json
import subprocess
import tempfile
warnings.filterwarnings('ignore')

def nvidia_asr_transcribe(audio_path):
    import nemo.collections.asr as nemo_asr
    model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
        model_name="nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0"
    )
    output = model.transcribe([audio_path])
    return output[0].text

def run_forced_aligner(audio_path, transcript):
    import torch
    from ctc_forced_aligner import (
        load_audio,
        load_alignment_model,
        generate_emissions,
        preprocess_text,
        get_alignments,
        get_spans,
        postprocess_results,
    )
    language = "ara"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = 16
    alignment_model, alignment_tokenizer = load_alignment_model(
        device,
        dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    audio_waveform = load_audio(audio_path, alignment_model.dtype, alignment_model.device)
    tokens_starred, text_starred = preprocess_text(
        transcript,
        romanize=True,
        language=language,
    )
    emissions, stride = generate_emissions(
        alignment_model, audio_waveform, batch_size=batch_size
    )
    segments, scores, blank_token = get_alignments(
        emissions,
        tokens_starred,
        alignment_tokenizer,
    )
    spans = get_spans(tokens_starred, segments, blank_token)
    word_timestamps = postprocess_results(text_starred, spans, stride, scores)
    return word_timestamps

def extract_segment(audio_path, start, end, out_path):
    audio = AudioSegment.from_wav(audio_path)
    segment = audio[int(start*1000):int(end*1000)]
    segment = segment.set_channels(1)
    segment = segment.set_frame_rate(16000)
    segment.export(out_path, format="wav")
    return out_path

def extract_features_from_audio(audio_file):
    y, sr = librosa.load(audio_file, sr=22050)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs, axis=1)
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr), axis=1)
    features = np.concatenate([
        mfccs_mean,                    # 13 features
        [spectral_centroid],           # 1 feature
        [spectral_rolloff],            # 1 feature
        [zero_crossing_rate],          # 1 feature
        [spectral_bandwidth],          # 1 feature
        spectral_contrast              # 7 features
    ])
    return features

def run_qalqalah_classifier(segment_path, model_path="falaq_word_model.pkl"):
    model = joblib.load(model_path)
    features = extract_features_from_audio(segment_path)
    features = features.reshape(1, -1)
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0] if hasattr(model, 'predict_proba') else None
    return prediction, proba

def main():
    # List of audio files to process 
    audio_files = [
        "all_audio_data/wav_audio_correct/Ayah_001.wav",
        # Add more files here for more trials
    ]
    for trial_idx, audio_path in enumerate(audio_files, 1):
        print(f"\n=== Trial {trial_idx}: {audio_path} ===")
        trial_dir = f"trial_{trial_idx}"
        os.makedirs(trial_dir, exist_ok=True)
        # 1. ASR
        transcript = nvidia_asr_transcribe(audio_path)
        print(f"ASR Transcript: {transcript}")
        # 2. Forced Alignment
        word_timestamps = run_forced_aligner(audio_path, transcript)
        print("Alignment results:")
        for i, word in enumerate(word_timestamps):
            print(word)
            # Save all segments
            safe_text = ''.join(c for c in word['text'] if c.isalnum() or c == '_')
            seg_path = os.path.join(trial_dir, f"segment_{i}_{safe_text}.wav")
            extract_segment(audio_path, word['start'], word['end'], seg_path)
        # 3. Qalqalah Classifier on segment 3 (4th word)
        if len(word_timestamps) > 3:
            falaq_word = word_timestamps[3]
            falaq_seg_path = os.path.join(trial_dir, f"segment_3_{''.join(c for c in falaq_word['text'] if c.isalnum() or c == '_')}.wav")
            prediction, proba = run_qalqalah_classifier(falaq_seg_path)
            result = {
                "prediction": int(prediction),
                "proba": proba.tolist() if proba is not None else None,
                "word": falaq_word['text'],
                "segment_path": falaq_seg_path
            }
            with open(os.path.join(trial_dir, "qalqalah_result.json"), "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Qalqalah classifier result: {result}")
        else:
            print("Not enough segments for Qalqalah classification.")

if __name__ == "__main__":
    main()