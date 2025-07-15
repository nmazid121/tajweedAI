#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract ALL FALAQ Words from ALL Reciters

Extracts the word الْفَلَقِ (Al-falaq) from every single reciter
in the extracted_timestamps folder and saves them to falaq_word_approach/positive_samples/
"""

import os
import json
import requests
from pydub import AudioSegment
import glob
from datetime import datetime

def download_audio_from_url(audio_url, start_time, end_time, output_path):
    """Download and extract audio segment from URL"""
    try:
        print(f"    📥 Downloading: {audio_url}")
        
        # Download the full audio file
        response = requests.get(audio_url, timeout=30)
        if response.status_code == 200:
            # Save temporary file
            temp_path = "temp_audio.mp3"
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            # Load with pydub
            audio = AudioSegment.from_mp3(temp_path)
            
            # Extract segment (times are in milliseconds)
            segment = audio[start_time:end_time]
            
            # Export segment
            segment.export(output_path, format="mp3")
            
            # Clean up temp file
            os.remove(temp_path)
            
            return True
        else:
            print(f"      ❌ Failed to download: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"      ❌ Error downloading: {e}")
        return False

def extract_falaq_from_reciter_timestamps(reciter_name, timestamps_file):
    """Extract falaq word from a specific reciter's timestamp file"""
    try:
        with open(timestamps_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get Ayah 1 data (Surah Falaq, Ayah 1)
        if '113' in data and '1' in data['113']:
            ayah_1 = data['113']['1']
        elif 'ayahs' in data and '1' in data['ayahs']:
            ayah_1 = data['ayahs']['1']
        else:
            print(f"    ❌ Ayah 1 not found in {reciter_name}")
            return False
        
        segments = ayah_1.get('segments', [])
        audio_url = ayah_1.get('audio_url', '')
        
        # الْفَلَقِ is the last word (segment 4 in Ayah 1)
        # Ayah 1: "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ"
        # Words: 1.قُلْ 2.أَعُوذُ 3.بِرَبِّ 4.الْفَلَقِ
        if len(segments) >= 4:
            falaq_segment = segments[3]  # 4th segment (index 3)
            start_time = int(falaq_segment[1])  # Start time in ms
            end_time = int(falaq_segment[2])    # End time in ms
            
            # Create output filename
            output_filename = f"{reciter_name}_falaq.mp3"
            output_path = os.path.join("falaq_word_approach", "positive_samples", output_filename)
            
            print(f"    🎵 Extracting falaq from {reciter_name}...")
            print(f"      Time: {start_time}ms - {end_time}ms")
            print(f"      Duration: {end_time - start_time}ms")
            
            # Try to download from URL
            if audio_url:
                success = download_audio_from_url(audio_url, start_time, end_time, output_path)
                if success:
                    print(f"      ✅ Success: {output_filename}")
                    return True
            
            print(f"      ❌ Failed to extract: {output_filename}")
            return False
        else:
            print(f"    ❌ Not enough segments in {reciter_name} Ayah 1")
            return False
            
    except Exception as e:
        print(f"    ❌ Error processing {timestamps_file}: {e}")
        return False

def get_reciter_name_from_folder(folder_name):
    """Convert folder name to readable reciter name"""
    # Remove _by_surah suffix
    name = folder_name.replace("_by_surah", "")
    
    # Convert to readable format
    name = name.replace("_", " ").title()
    
    return name

def main():
    """Main extraction function"""
    print("🎯 EXTRACT ALL FALAQ WORDS FROM ALL RECITERS")
    print("=" * 60)
    print("Extracting الْفَلَقِ from every single reciter...")
    print()
    
    # Create output directory
    os.makedirs("falaq_word_approach/positive_samples", exist_ok=True)
    
    # Find all reciter folders in extracted_timestamps
    reciter_folders = glob.glob("extracted_timestamps/*_by_surah")
    
    if not reciter_folders:
        print("❌ No reciter folders found in extracted_timestamps!")
        return
    
    print(f"Found {len(reciter_folders)} reciter folders")
    
    # Extract from each reciter
    successful_extractions = 0
    failed_extractions = 0
    
    for reciter_folder in reciter_folders:
        # Get reciter name
        folder_name = os.path.basename(reciter_folder)
        reciter_name = get_reciter_name_from_folder(folder_name)
        
        # Find the Al-Falaq timestamps file
        falaq_timestamps_file = os.path.join(reciter_folder, "113_Al-Falaq_timestamps.json")
        
        if os.path.exists(falaq_timestamps_file):
            print(f"\n📁 Processing: {reciter_name}")
            print(f"   File: {falaq_timestamps_file}")
            
            success = extract_falaq_from_reciter_timestamps(reciter_name, falaq_timestamps_file)
            if success:
                successful_extractions += 1
            else:
                failed_extractions += 1
        else:
            print(f"\n❌ Al-Falaq timestamps not found for: {reciter_name}")
            failed_extractions += 1
    
    print(f"\n" + "=" * 60)
    print("🎉 EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"✅ Successfully extracted: {successful_extractions}")
    print(f"❌ Failed extractions: {failed_extractions}")
    print(f"📁 Files saved to: falaq_word_approach/positive_samples/")
    print(f"📊 Total reciters processed: {len(reciter_folders)}")
    
    if successful_extractions > 0:
        print(f"\n🎯 You now have {successful_extractions} expert recitations of الْفَلَقِ!")
        print("Next step: Record your incorrect versions for negative samples.")
        
        # List the extracted files
        print(f"\n📋 Extracted files:")
        positive_samples_dir = "falaq_word_approach/positive_samples"
        if os.path.exists(positive_samples_dir):
            files = [f for f in os.listdir(positive_samples_dir) if f.endswith('.mp3')]
            for file in sorted(files):
                print(f"   ✅ {file}")

if __name__ == "__main__":
    main()