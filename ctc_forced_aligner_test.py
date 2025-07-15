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

# === CHANGE THESE ===
audio_path = "wav_audio_correct/Ayah_001.wav"
text = "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ"  # Or your ASR output
language = "ara"  # ISO-639-3 code for Arabic

print(f"DEBUG: About to load audio file: {audio_path}")
import os
print(f"DEBUG: File exists? {os.path.exists(audio_path)}")

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16

try:
    print("DEBUG: Loading alignment model...")
    alignment_model, alignment_tokenizer = load_alignment_model(
        device,
        dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    print("DEBUG: Loading audio...")
    audio_waveform = load_audio(audio_path, alignment_model.dtype, alignment_model.device)

    print("DEBUG: Preprocessing text...")
    tokens_starred, text_starred = preprocess_text(
        text,
        romanize=True,
        language=language,
    )

    print("DEBUG: Generating emissions...")
    emissions, stride = generate_emissions(
        alignment_model, audio_waveform, batch_size=batch_size
    )

    print("DEBUG: Getting alignments...")
    segments, scores, blank_token = get_alignments(
        emissions,
        tokens_starred,
        alignment_tokenizer,
    )

    print("DEBUG: Getting spans...")
    spans = get_spans(tokens_starred, segments, blank_token)

    print("DEBUG: Postprocessing results...")
    word_timestamps = postprocess_results(text_starred, spans, stride, scores)

    print("Alignment results:")
    for i, word in enumerate(word_timestamps):
        print(word)

    # Save each segment as a separate WAV file using pydub
    from pydub import AudioSegment
    orig_audio = AudioSegment.from_wav(audio_path)
    for i, word in enumerate(word_timestamps):
        start_ms = int(word['start'] * 1000)
        end_ms = int(word['end'] * 1000)
        segment = orig_audio[start_ms:end_ms]
        # Clean text for filename
        safe_text = ''.join(c for c in word['text'] if c.isalnum() or c == '_')
        out_path = f"segment_{i}_{safe_text}.wav"
        segment.export(out_path, format="wav")
        print(f"Saved: {out_path}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()