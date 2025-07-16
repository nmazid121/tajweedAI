import json
import csv
import os
import requests
from pathlib import Path
from pydub import AudioSegment
import tempfile
import shutil

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

def extract_segment_from_timestamps(audio_path, start_time, end_time, output_dir, reciter, surah, ayah):
    """
    Extract audio segment using existing timestamps
    """
    try:
        print(f"Processing: {reciter} - Surah {surah}:{ayah}")
        
        # Load audio file - handle both MP3 and WAV
        if audio_path.lower().endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_path)
        else:
            audio = AudioSegment.from_wav(audio_path)
        
        # Convert timestamps from milliseconds to milliseconds (they're already in ms)
        start_ms = int(start_time)
        end_ms = int(end_time)
        
        # Extract segment
        segment = audio[start_ms:end_ms]
        
        # Create output filename
        safe_reciter = reciter.replace('-', '_').replace(' ', '_')
        output_filename = f"{safe_reciter}_s{surah:03d}a{ayah:03d}_qalqalah.wav"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save the segment
        segment.export(output_path, format="wav")
        
        duration_sec = (end_ms - start_ms) / 1000.0
        print(f"  Extracted: {output_filename} ({start_ms}-{end_ms}ms, {duration_sec:.2f}s)")
        
        return {
            'reciter': reciter,
            'surah': surah,
            'ayah': ayah,
            'start_time_ms': start_ms,
            'end_time_ms': end_ms,
            'duration_sec': duration_sec,
            'output_file': output_filename
        }
        
    except Exception as e:
        print(f"  Error processing {reciter} - Surah {surah}:{ayah}: {e}")
        return None

def main():
    """Main function to extract Qalqalah audio segments using existing timestamps"""
    
    # Define paths
    base_dir = Path("extracted_timestamps/surah_falaq_inshiqaq/selected_ayahs/ctc-forced-aligner-inputs")
    csv_file = base_dir / "last_word_segments.csv"
    output_dir = base_dir / "extracted_qalqalah_segments_simple"
    
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
        
        print(f"Processing {len(segments)} segments using existing timestamps...")
        print("=" * 60)
        
        # Process each segment
        for i, segment in enumerate(segments):
            reciter = segment['reciter']
            surah_num = int(segment['surah_number'])
            ayah_num = int(segment['ayah_number'])
            audio_url = segment['audio_url']
            start_time = int(segment['start_time'])
            end_time = int(segment['end_time'])
            
            print(f"\n[{i+1}/{len(segments)}] Processing {reciter} - Surah {surah_num}:{ayah_num}")
            
            # Download audio file as MP3 (since URLs point to MP3 files)
            audio_filename = f"{reciter}_s{surah_num:03d}a{ayah_num:03d}.mp3"
            audio_path = temp_dir / audio_filename
            
            if not download_audio_file(audio_url, audio_path):
                print(f"  Skipping due to download failure")
                continue
            
            # Extract segment using timestamps
            result = extract_segment_from_timestamps(
                str(audio_path),
                start_time,
                end_time,
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
            durations = [r['duration_sec'] for r in results]
            print(f"Average duration: {sum(durations)/len(durations):.2f}s")
            print(f"Min duration: {min(durations):.2f}s")
            print(f"Max duration: {max(durations):.2f}s")
            
            # Group by reciter
            reciter_counts = {}
            for r in results:
                reciter = r['reciter']
                reciter_counts[reciter] = reciter_counts.get(reciter, 0) + 1
            
            print(f"\nSegments per reciter:")
            for reciter, count in sorted(reciter_counts.items()):
                print(f"  {reciter}: {count} segments")
        
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Extracting Qalqalah audio segments using existing timestamps...")
    main() 