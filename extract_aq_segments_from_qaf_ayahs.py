import os
import json
import subprocess
import shutil
from pathlib import Path
import soundfile as sf
import numpy as np

def find_qaf_ending_ayahs(quran_metadata_path):
    """Find ayahs that end with Qaf (ق)"""
    qaf_ayahs = []
    
    try:
        with open(quran_metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for surah in data:
            for ayah in surah['ayahs']:
                text = ayah['text']
                # Check if ayah ends with Qaf
                if text.strip().endswith('ق'):
                    qaf_ayahs.append({
                        'surah': surah['number'],
                        'ayah': ayah['number'],
                        'text': text,
                        'surah_name': surah['name']
                    })
                    
    except Exception as e:
        print(f"Error reading Quran metadata: {e}")
        return []
    
    return qaf_ayahs

def get_audio_file_path(reciter, surah_num, ayah_num, audio_base_path):
    """Get the path to the audio file for a specific ayah"""
    # Common audio file naming patterns
    possible_paths = [
        f"{audio_base_path}/{reciter}/surah_{surah_num:03d}/ayah_{ayah_num:03d}.wav",
        f"{audio_base_path}/{reciter}/surah_{surah_num:03d}/ayah_{ayah_num}.wav",
        f"{audio_base_path}/{reciter}/surah_{surah_num}/ayah_{ayah_num}.wav",
        f"{audio_base_path}/{reciter}/surah_{surah_num:03d}_{ayah_num:03d}.wav",
        f"{audio_base_path}/{reciter}/surah_{surah_num}_{ayah_num}.wav"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def convert_to_mono_wav(input_path, output_path):
    """Convert audio to mono WAV format"""
    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            '-ar', '44100',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False

def extract_aq_segment_with_aligner(audio_path, text, output_path, window_ms=100):
    """Extract the 'aq' segment using CTC forced aligner"""
    
    # Create temporary directory for aligner
    temp_dir = "temp_aligner_work"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Copy audio to temp directory
        temp_audio = os.path.join(temp_dir, "audio.wav")
        shutil.copy2(audio_path, temp_audio)
        
        # Create text file for alignment
        text_file = os.path.join(temp_dir, "text.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Run CTC forced aligner
        cmd = [
            'ctc-forced-aligner',
            '--audio', temp_audio,
            '--text', text_file,
            '--output', temp_dir
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Aligner failed: {result.stderr}")
            return False
        
        # Read alignment results
        alignment_file = os.path.join(temp_dir, "alignment.json")
        if not os.path.exists(alignment_file):
            print("Alignment file not found")
            return False
        
        with open(alignment_file, 'r', encoding='utf-8') as f:
            alignment = json.load(f)
        
        # Find the last word (Qaf) timing
        words = alignment.get('words', [])
        if not words:
            print("No words found in alignment")
            return False
        
        # Get the last word timing (should be Qaf)
        last_word = words[-1]
        start_time = last_word.get('start', 0)
        end_time = last_word.get('end', 0)
        
        # Extract segment with window
        window_seconds = window_ms / 1000.0
        segment_start = max(0, start_time - window_seconds)
        segment_end = end_time + window_seconds
        
        # Load audio and extract segment
        audio_data, sample_rate = sf.read(temp_audio)
        start_sample = int(segment_start * sample_rate)
        end_sample = int(segment_end * sample_rate)
        
        segment = audio_data[start_sample:end_sample]
        
        # Save extracted segment
        sf.write(output_path, segment, sample_rate)
        
        return True
        
    except Exception as e:
        print(f"Error extracting segment: {e}")
        return False
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    # Configuration
    quran_metadata_path = "qul_downloads/quran-ayah-data/quran-data.json"  # Adjust path as needed
    audio_base_path = "download_script/downloaded_quran_audio_direct"  # Adjust path as needed
    output_dir = "extracted_aq_segments"
    reciters = ["mishary", "abdul_basit", "husary", "maher", "minshawi", "shuraim", "yasser"]
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find Qaf-ending ayahs
    print("Finding ayahs ending with Qaf...")
    qaf_ayahs = find_qaf_ending_ayahs(quran_metadata_path)
    
    if not qaf_ayahs:
        print("No Qaf-ending ayahs found. Please check the metadata file path.")
        return
    
    print(f"Found {len(qaf_ayahs)} ayahs ending with Qaf")
    
    # Process each ayah for each reciter
    successful_extractions = 0
    total_attempts = 0
    
    for ayah_info in qaf_ayahs:
        surah_num = ayah_info['surah']
        ayah_num = ayah_info['ayah']
        text = ayah_info['text']
        surah_name = ayah_info['surah_name']
        
        print(f"\nProcessing {surah_name} Ayah {ayah_num}: {text}")
        
        for reciter in reciters:
            total_attempts += 1
            
            # Find audio file
            audio_path = get_audio_file_path(reciter, surah_num, ayah_num, audio_base_path)
            
            if not audio_path:
                print(f"  {reciter}: Audio file not found")
                continue
            
            print(f"  {reciter}: Found audio file")
            
            # Create output filename
            output_filename = f"{reciter}_surah_{surah_num:03d}_ayah_{ayah_num:03d}_aq.wav"
            output_path = os.path.join(output_dir, output_filename)
            
            # Convert to mono WAV if needed
            temp_audio = audio_path
            if not audio_path.lower().endswith('.wav'):
                temp_audio = audio_path.replace('.mp3', '_temp.wav')
                if not convert_to_mono_wav(audio_path, temp_audio):
                    print(f"  {reciter}: Failed to convert audio")
                    continue
            
            # Extract 'aq' segment
            if extract_aq_segment_with_aligner(temp_audio, text, output_path):
                print(f"  {reciter}: ✓ Successfully extracted 'aq' segment")
                successful_extractions += 1
            else:
                print(f"  {reciter}: ✗ Failed to extract segment")
            
            # Clean up temp file
            if temp_audio != audio_path and os.path.exists(temp_audio):
                os.remove(temp_audio)
    
    print(f"\nExtraction complete!")
    print(f"Successful extractions: {successful_extractions}/{total_attempts}")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main() 