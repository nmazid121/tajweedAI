import json
import csv
import os
import requests
import torch
from pathlib import Path
from pydub import AudioSegment
import tempfile
import shutil
from ctc_forced_aligner import (
    load_audio,
    load_alignment_model,
    generate_emissions,
    preprocess_text,
    get_alignments,
    get_spans,
    postprocess_results,
)

def download_audio_file(url, output_path):
    """Download audio file from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_last_word_with_ctc(audio_path, text, output_dir, reciter, surah, ayah):
    """
    Use CTC forced aligner to extract the last word from an ayah
    """
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        batch_size = 16
        
        print(f"Processing: {reciter} - Surah {surah}:{ayah}")
        
        # Load alignment model
        alignment_model, alignment_tokenizer = load_alignment_model(
            device,
            dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        
        # Load audio
        audio_waveform = load_audio(audio_path, alignment_model.dtype, alignment_model.device)
        
        # Preprocess text
        tokens_starred, text_starred = preprocess_text(
            text,
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
        
        if not word_timestamps:
            print(f"  Warning: No words found for {reciter} - Surah {surah}:{ayah}")
            return None
        
        # Get the last word
        last_word = word_timestamps[-1]
        
        # Extract the audio segment
        orig_audio = AudioSegment.from_wav(audio_path)
        start_ms = int(last_word['start'] * 1000)
        end_ms = int(last_word['end'] * 1000)
        segment = orig_audio[start_ms:end_ms]
        
        # Create output filename
        safe_reciter = reciter.replace('-', '_').replace(' ', '_')
        safe_text = ''.join(c for c in last_word['text'] if c.isalnum() or c == '_')
        output_filename = f"{safe_reciter}_s{surah:03d}a{ayah:03d}_{safe_text}.wav"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save the segment
        segment.export(output_path, format="wav")
        
        print(f"  Extracted: {output_filename} ({start_ms}-{end_ms}ms)")
        
        return {
            'reciter': reciter,
            'surah': surah,
            'ayah': ayah,
            'word_text': last_word['text'],
            'start_time': last_word['start'],
            'end_time': last_word['end'],
            'duration': last_word['end'] - last_word['start'],
            'output_file': output_filename
        }
        
    except Exception as e:
        print(f"  Error processing {reciter} - Surah {surah}:{ayah}: {e}")
        return None

def main():
    """Main function to extract Qalqalah audio segments"""
    
    # Define paths
    base_dir = Path("extracted_timestamps/surah_falaq_inshiqaq/selected_ayahs/ctc-forced-aligner-inputs")
    csv_file = base_dir / "last_word_segments.csv"
    output_dir = base_dir / "extracted_qalqalah_segments"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Create temporary directory for downloads
    temp_dir = Path(tempfile.mkdtemp())
    
    # Store results
    results = []
    
    try:
        # Read CSV file
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            segments = list(reader)
        
        print(f"Processing {len(segments)} segments...")
        print("=" * 60)
        
        # Process each segment
        for i, segment in enumerate(segments):
            reciter = segment['reciter']
            surah_num = int(segment['surah_number'])
            ayah_num = int(segment['ayah_number'])
            audio_url = segment['audio_url']
            
            print(f"\n[{i+1}/{len(segments)}] Processing {reciter} - Surah {surah_num}:{ayah_num}")
            
            # Download audio file
            audio_filename = f"{reciter}_s{surah_num:03d}a{ayah_num:03d}.wav"
            audio_path = temp_dir / audio_filename
            
            if not download_audio_file(audio_url, audio_path):
                print(f"  Skipping due to download failure")
                continue
            
            # Define the text for the ayah (you'll need to provide this)
            # For now, we'll use a placeholder - you should replace this with actual ayah text
            if surah_num == 113:  # Al-Falaq
                if ayah_num == 1:
                    text = "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ"
                elif ayah_num == 2:
                    text = "مِن شَرِّ مَا خَلَقَ"
            elif surah_num == 84:  # Al-Inshiqaq
                if ayah_num == 16:
                    text = "فَلَا أُقْسِمُ بِالشَّفَقِ"
                elif ayah_num == 17:
                    text = "وَاللَّيْلِ وَمَا وَسَقَ"
                elif ayah_num == 18:
                    text = "وَالْقَمَرِ إِذَا اتَّسَقَ"
                elif ayah_num == 19:
                    text = "لَتَرْكَبُنَّ طَبَقًا عَن طَبَقٍ"
            else:
                print(f"  Warning: No text defined for Surah {surah_num}:{ayah_num}")
                continue
            
            # Extract last word using CTC aligner
            result = extract_last_word_with_ctc(
                str(audio_path), 
                text, 
                str(output_dir), 
                reciter, 
                surah_num, 
                ayah_num
            )
            
            if result:
                results.append(result)
            
            # Clean up downloaded file
            if audio_path.exists():
                audio_path.unlink()
        
        # Save results summary
        results_file = output_dir / "extraction_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Create CSV summary
        csv_results_file = output_dir / "extraction_results.csv"
        with open(csv_results_file, 'w', encoding='utf-8', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        print(f"\n=== EXTRACTION COMPLETE ===")
        print(f"Successfully extracted: {len(results)} segments")
        print(f"Output directory: {output_dir}")
        print(f"Results saved to: {results_file}")
        print(f"CSV summary: {csv_results_file}")
        
        # Show some statistics
        if results:
            durations = [r['duration'] for r in results]
            print(f"Average duration: {sum(durations)/len(durations):.2f}s")
            print(f"Min duration: {min(durations):.2f}s")
            print(f"Max duration: {max(durations):.2f}s")
        
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Extracting Qalqalah audio segments using CTC forced aligner...")
    main() 