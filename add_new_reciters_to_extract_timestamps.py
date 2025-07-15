#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add New Reciters to Existing extracted_timestamps Folder

Processes the massive JSON files in qul_downloads/audio/all_reciters_json/
and adds them to the existing extracted_timestamps folder structure.
"""

import json
import os
import csv
from datetime import datetime

# Configuration
INPUT_DIR = "qul_downloads/audio/all_reciters_json"
OUTPUT_DIR = "extracted_timestamps"

# Surahs to extract timestamps for (focusing on Al-Falaq)
SURAH_NUMBERS_TO_EXTRACT = [113]  # Al-Falaq only

SURAH_NUMBER_TO_NAME = {
    113: "Al-Falaq"
}

def load_json_data(file_path):
    """Load JSON data from file."""
    try:
        print(f"  Loading {os.path.basename(file_path)}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return None

def extract_timestamps_from_json(json_data, reciter_name):
    """Extract timestamp data for specified surahs."""
    timestamps_data = {}
    
    for key, ayah_info in json_data.items():
        if isinstance(ayah_info, dict):
            surah_number = ayah_info.get("surah_number")
            if surah_number in SURAH_NUMBERS_TO_EXTRACT:
                ayah_number = ayah_info.get("ayah_number")
                segments = ayah_info.get("segments", [])
                audio_url = ayah_info.get("audio_url")
                
                if surah_number not in timestamps_data:
                    timestamps_data[surah_number] = {}
                
                timestamps_data[surah_number][ayah_number] = {
                    "segments": segments,
                    "audio_url": audio_url,
                    "reciter": reciter_name
                }
    
    return timestamps_data

def save_timestamps_by_surah(timestamps_data, output_dir, reciter_name):
    """Save timestamps data organized by surah."""
    reciter_dir = os.path.join(output_dir, f"{reciter_name.lower().replace(' ', '_').replace('-', '_')}_by_surah")
    os.makedirs(reciter_dir, exist_ok=True)
    
    for surah_num in sorted(timestamps_data.keys()):
        surah_name = SURAH_NUMBER_TO_NAME.get(surah_num, f"Surah_{surah_num}")
        surah_file = os.path.join(reciter_dir, f"{surah_num:03d}_{surah_name}_timestamps.json")
        
        surah_data = {
            "surah_number": surah_num,
            "surah_name": surah_name,
            "ayahs": timestamps_data[surah_num]
        }
        
        with open(surah_file, 'w', encoding='utf-8') as f:
            json.dump(surah_data, f, indent=2, ensure_ascii=False)
        
        print(f"    Saved {surah_name} timestamps to: {surah_file}")

def save_timestamps_as_json(timestamps_data, output_file):
    """Save timestamps data as JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(timestamps_data, f, indent=2, ensure_ascii=False)
    print(f"    Saved timestamps to: {output_file}")

def save_timestamps_as_csv(timestamps_data, output_file, reciter_name):
    """Save timestamps data as CSV for easy analysis."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['surah_number', 'surah_name', 'ayah_number', 'reciter', 'word_number', 'start_time_ms', 'end_time_ms', 'duration_ms', 'audio_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for surah_num in sorted(timestamps_data.keys()):
            surah_name = SURAH_NUMBER_TO_NAME.get(surah_num, f"Surah_{surah_num}")
            
            for ayah_num in sorted(timestamps_data[surah_num].keys()):
                ayah_data = timestamps_data[surah_num][ayah_num]
                segments = ayah_data["segments"]
                audio_url = ayah_data["audio_url"]
                
                for segment in segments:
                    if len(segment) >= 3:
                        word_num = segment[0]
                        start_time = int(segment[1])  # Convert to int
                        end_time = int(segment[2])    # Convert to int
                        duration = end_time - start_time
                        
                        writer.writerow({
                            'surah_number': surah_num,
                            'surah_name': surah_name,
                            'ayah_number': ayah_num,
                            'reciter': reciter_name,
                            'word_number': word_num,
                            'start_time_ms': start_time,
                            'end_time_ms': end_time,
                            'duration_ms': duration,
                            'audio_url': audio_url
                        })
    
    print(f"    Saved timestamps CSV to: {output_file}")

def create_word_level_summary(timestamps_data, output_file, reciter_name):
    """Create a summary of word-level statistics."""
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "reciter": reciter_name,
        "total_surahs": len(timestamps_data),
        "total_ayahs": sum(len(surah_data) for surah_data in timestamps_data.values()),
        "total_words": 0,
        "surah_summary": {}
    }
    
    for surah_num in sorted(timestamps_data.keys()):
        surah_name = SURAH_NUMBER_TO_NAME.get(surah_num, f"Surah_{surah_num}")
        ayahs = timestamps_data[surah_num]
        
        surah_words = sum(len(ayah_data["segments"]) for ayah_data in ayahs.values())
        summary["total_words"] += surah_words
        
        summary["surah_summary"][surah_num] = {
            "name": surah_name,
            "ayah_count": len(ayahs),
            "word_count": surah_words
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"    Saved summary to: {output_file}")

def get_reciter_name_from_filename(filename):
    """Extract reciter name from filename."""
    # Remove prefix and suffix
    name = filename.replace("ayah-recitation-", "").replace(".json", "")
    
    # Handle different naming patterns
    if "murattal-hafs-" in name:
        name = name.replace("-murattal-hafs-", "_")
    elif "mujawwad-hafs-" in name:
        name = name.replace("-mujawwad-hafs-", "_")
    elif "recitation-murattal-hafs-" in name:
        name = name.replace("-recitation-murattal-hafs-", "_")
    elif "recitation.json" in name:
        name = name.replace("-recitation", "")
    
    # Remove the ID number at the end
    if "_" in name and name.split("_")[-1].isdigit():
        name = "_".join(name.split("_")[:-1])
    
    # Convert to readable format
    name = name.replace("-", " ").replace("_", " ").title()
    
    return name

def main():
    """Main function to extract timestamps from all reciters."""
    print("Adding new reciters to existing extracted_timestamps folder...")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Focusing on: {[SURAH_NUMBER_TO_NAME[s] for s in SURAH_NUMBERS_TO_EXTRACT]}")
    print()
    
    # Check if output directory exists
    if not os.path.exists(OUTPUT_DIR):
        print(f"❌ Output directory {OUTPUT_DIR} does not exist!")
        return
    
    # Get all JSON files
    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    
    if not json_files:
        print(f"❌ No JSON files found in {INPUT_DIR}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    successful_extractions = 0
    
    for json_file in json_files:
        file_path = os.path.join(INPUT_DIR, json_file)
        reciter_name = get_reciter_name_from_filename(json_file)
        
        print(f"\n📁 Processing: {reciter_name}")
        print(f"   File: {json_file}")
        
        # Load and process JSON data
        json_data = load_json_data(file_path)
        if json_data:
            timestamps = extract_timestamps_from_json(json_data, reciter_name)
            
            if timestamps:
                print(f"   ✅ Extracted timestamps for {len(timestamps)} surahs")
                
                # Save by surah
                save_timestamps_by_surah(timestamps, OUTPUT_DIR, reciter_name)
                
                # Save main JSON file
                json_file_path = os.path.join(OUTPUT_DIR, f"{reciter_name.lower().replace(' ', '_').replace('-', '_')}_timestamps.json")
                save_timestamps_as_json(timestamps, json_file_path)
                
                # Save CSV file
                csv_file_path = os.path.join(OUTPUT_DIR, f"{reciter_name.lower().replace(' ', '_').replace('-', '_')}_timestamps.csv")
                save_timestamps_as_csv(timestamps, csv_file_path, reciter_name)
                
                # Save summary
                summary_file = os.path.join(OUTPUT_DIR, f"{reciter_name.lower().replace(' ', '_').replace('-', '_')}_summary.json")
                create_word_level_summary(timestamps, summary_file, reciter_name)
                
                successful_extractions += 1
            else:
                print(f"   ❌ No matching surahs found")
        else:
            print(f"   ❌ Failed to load JSON data")
    
    print(f"\n🎉 EXTRACTION COMPLETE!")
    print(f"✅ Successfully processed: {successful_extractions}/{len(json_files)} reciters")
    print(f" All files added to: {OUTPUT_DIR}")
    print(f"\nNow you can run the falaq_word_extractor.py script again to get ALL reciters!")

if __name__ == "__main__":
    main()