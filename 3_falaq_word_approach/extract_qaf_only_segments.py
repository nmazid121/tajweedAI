import os
from pathlib import Path
from pydub import AudioSegment
from ctc_forced_aligner import (
    load_audio,
    load_alignment_model,
    generate_emissions,
    preprocess_text,
    get_alignments,
    get_spans,
    postprocess_results,
)
import torch
import re

# Ayah text mapping
AYAH_TEXTS = {
    (113, 1): "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
    (113, 2): "مِن شَرِّ مَا خَلَقَ",
    (84, 16): "فَلَا أُقْسِمُ بِالشَّفَقِ",
    (84, 17): "وَاللَّيْلِ وَمَا وَسَقَ",
    (84, 18): "وَالْقَمَرِ إِذَا اتَّسَقَ",
    (84, 19): "لَتَرْكَبُنَّ طَبَقًا عَن طَبَقٍ",
}

# Window size in ms
WINDOW_BEFORE = 100
WINDOW_AFTER = 200

INPUT_DIR = Path("3_falaq_word_approach/positive_samples_qalqalah_kubra")
OUTPUT_DIR = Path("3_falaq_word_approach/positive_samples_qaf_only")
OUTPUT_DIR.mkdir(exist_ok=True)

def ensure_mono_wav(audio_path):
    """Ensure the file is mono WAV. If not, convert and return new path."""
    audio = AudioSegment.from_wav(audio_path)
    if audio.channels == 1:
        return audio_path
    # Convert to mono
    mono_audio = audio.set_channels(1)
    tmp_path = audio_path.parent / (audio_path.stem + "_mono.wav")
    mono_audio.export(tmp_path, format="wav")
    return tmp_path

def extract_qaf_segment(audio_path, ayah_text, output_path):
    # Ensure mono WAV
    audio_path = ensure_mono_wav(audio_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = 16
    # Load alignment model
    alignment_model, alignment_tokenizer = load_alignment_model(
        device,
        dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    # Load audio
    audio_waveform = load_audio(str(audio_path), alignment_model.dtype, alignment_model.device)
    # Preprocess text
    tokens_starred, text_starred = preprocess_text(
        ayah_text,
        romanize=True,
        language="ara",
    )
    # Generate emissions
    emissions, stride = generate_emissions(
        alignment_model, audio_waveform, batch_size=batch_size
    )
    # Get alignments
    segments, scores, blank_token = get_alignments(
        emissions,
        tokens_starred,
        alignment_tokenizer,
    )
    # Get spans
    spans = get_spans(tokens_starred, segments, blank_token)
    # Postprocess results
    word_timestamps = postprocess_results(text_starred, spans, stride, scores)
    # Find the last Qaf (ق) in the alignment
    qaf_index = None
    for i in reversed(range(len(word_timestamps))):
        if "ق" in word_timestamps[i]['text']:
            qaf_index = i
            break
    if qaf_index is None:
        print(f"  Qaf not found in alignment for {audio_path.name}")
        return False
    qaf_word = word_timestamps[qaf_index]
    # Use the full word containing Qaf (usually the last word)
    start_ms = int(qaf_word['start'] * 1000) - WINDOW_BEFORE
    end_ms = int(qaf_word['end'] * 1000) + WINDOW_AFTER
    # Load original audio
    audio = AudioSegment.from_wav(audio_path)
    # Clip to audio bounds
    start_ms = max(0, start_ms)
    end_ms = min(len(audio), end_ms)
    segment = audio[start_ms:end_ms]
    segment.export(output_path, format="wav")
    print(f"  Extracted Qaf segment: {output_path.name} ({start_ms}-{end_ms}ms)")
    # Clean up temp mono file if created
    if audio_path.stem.endswith('_mono'):
        os.remove(audio_path)
    return True

def main():
    files = list(INPUT_DIR.glob("*.wav"))
    print(f"Found {len(files)} files to process.")
    extracted = 0
    for file in files:
        # Parse surah and ayah from filename using regex
        match = re.search(r's(\d{3})a(\d{3})', file.stem)
        if not match:
            print(f"  Could not parse surah/ayah from {file.name}, skipping.")
            continue
        surah = int(match.group(1))
        ayah = int(match.group(2))
        ayah_text = AYAH_TEXTS.get((surah, ayah))
        if not ayah_text:
            print(f"  No ayah text for {file.name}, skipping.")
            continue
        output_path = OUTPUT_DIR / (file.stem + "_qaf.wav")
        try:
            if extract_qaf_segment(file, ayah_text, output_path):
                extracted += 1
        except Exception as e:
            print(f"  Error processing {file.name}: {e}")
    print(f"\nDone! Extracted {extracted} Qaf segments to {OUTPUT_DIR}")

if __name__ == "__main__":
    print("Extracting Qaf-only segments from positive samples...")
    main() 