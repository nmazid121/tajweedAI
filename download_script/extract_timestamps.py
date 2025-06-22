import json
import os
import csv
from datetime import datetime

# Configuration
HUSARY_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\download_script\ayah-recitation-mahmoud-khalil-al-husary-murattal-hafs-957.json'
MINSHAWI_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\Husary\Husarry Murattal\ayah-recitation-muhammad-siddiq-al-minshawi-murattal-hafs-959.json\ayah-recitation-muhammad-siddiq-al-minshawi-murattal-hafs-959.json'
ABDUL_BASIT_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\ayah-recitation-abdul-basit-abdul-samad-murattal-hafs-950.json\ayah-recitation-abdul-basit-abdul-samad-murattal-hafs-950.json'
MISHARY_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\ayah-recitation-mishari-rashid-al-afasy-murattal-hafs-953.json\ayah-recitation-mishari-rashid-al-afasy-murattal-hafs-953.json'
MAHER_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\ayah-recitation-maher-al-mu-aiqly-murattal-hafs-948.json\ayah-recitation-maher-al-mu-aiqly-murattal-hafs-948.json'
YASSER_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\ayah-recitation-yasser-al-dosari-murattal-hafs-961.json\ayah-recitation-yasser-al-dosari-murattal-hafs-961.json'
SHURAIM_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\ayah-recitation-saud-al-shuraim-murattal-hafs-960.json\ayah-recitation-saud-al-shuraim-murattal-hafs-960.json'

# Surahs to extract timestamps for
SURAH_NUMBERS_TO_EXTRACT = [
    1,   # Al-Fatiha
    111, # Al-Lahab
    112, # Al-Ikhlas
    113, # Al-Falaq
    109, # Al-Kafirun
    82   # Al-Infitar
]

SURAH_NUMBER_TO_NAME = {
    1: "Al-Fatiha",
    111: "Al-Lahab",
    112: "Al-Ikhlas",
    113: "Al-Falaq",
    109: "Al-Kafirun",
    82: "Al-Infitar"
}

def load_json_data(file_path):
    """Load JSON data from file."""
    try:
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

def save_timestamps_as_json(timestamps_data, output_file):
    """Save timestamps data as JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(timestamps_data, f, indent=2, ensure_ascii=False)
    print(f"Saved timestamps to: {output_file}")

def save_timestamps_as_csv(timestamps_data, output_file):
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
                reciter = ayah_data["reciter"]
                audio_url = ayah_data["audio_url"]
                
                for segment in segments:
                    if len(segment) >= 3:
                        word_num, start_time, end_time = segment[0], segment[1], segment[2]
                        duration = end_time - start_time
                        
                        writer.writerow({
                            'surah_number': surah_num,
                            'surah_name': surah_name,
                            'ayah_number': ayah_num,
                            'reciter': reciter,
                            'word_number': word_num,
                            'start_time_ms': start_time,
                            'end_time_ms': end_time,
                            'duration_ms': duration,
                            'audio_url': audio_url
                        })
    
    print(f"Saved timestamps CSV to: {output_file}")

def save_timestamps_by_surah(timestamps_data, output_dir):
    """Save timestamps data organized by surah."""
    os.makedirs(output_dir, exist_ok=True)
    
    for surah_num in sorted(timestamps_data.keys()):
        surah_name = SURAH_NUMBER_TO_NAME.get(surah_num, f"Surah_{surah_num}")
        surah_file = os.path.join(output_dir, f"{surah_num:03d}_{surah_name}_timestamps.json")
        
        surah_data = {
            "surah_number": surah_num,
            "surah_name": surah_name,
            "ayahs": timestamps_data[surah_num]
        }
        
        with open(surah_file, 'w', encoding='utf-8') as f:
            json.dump(surah_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {surah_name} timestamps to: {surah_file}")

def create_word_level_summary(timestamps_data, output_file):
    """Create a summary of word-level statistics."""
    summary = {
        "extraction_date": datetime.now().isoformat(),
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
    
    print(f"Saved summary to: {output_file}")

def main():
    """Main function to extract timestamps from both reciters."""
    print("Extracting word-level timestamps from Quran JSON files...")
    
    # Create output directory
    output_dir = "extracted_timestamps"
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract from Husary
    print("\nProcessing Husary JSON...")
    husary_data = load_json_data(HUSARY_JSON_PATH)
    if husary_data:
        husary_timestamps = extract_timestamps_from_json(husary_data, "Husary")
        print(f"Extracted timestamps for {len(husary_timestamps)} surahs from Husary")
        
        # Save Husary timestamps
        save_timestamps_as_json(husary_timestamps, os.path.join(output_dir, "husary_timestamps.json"))
        save_timestamps_as_csv(husary_timestamps, os.path.join(output_dir, "husary_timestamps.csv"))
        save_timestamps_by_surah(husary_timestamps, os.path.join(output_dir, "husary_by_surah"))
        create_word_level_summary(husary_timestamps, os.path.join(output_dir, "husary_summary.json"))
    
    # Extract from Minshawi
    print("\nProcessing Minshawi JSON...")
    minshawi_data = load_json_data(MINSHAWI_JSON_PATH)
    if minshawi_data:
        minshawi_timestamps = extract_timestamps_from_json(minshawi_data, "Minshawi")
        print(f"Extracted timestamps for {len(minshawi_timestamps)} surahs from Minshawi")
        
        # Save Minshawi timestamps
        save_timestamps_as_json(minshawi_timestamps, os.path.join(output_dir, "minshawi_timestamps.json"))
        save_timestamps_as_csv(minshawi_timestamps, os.path.join(output_dir, "minshawi_timestamps.csv"))
        save_timestamps_by_surah(minshawi_timestamps, os.path.join(output_dir, "minshawi_by_surah"))
        create_word_level_summary(minshawi_timestamps, os.path.join(output_dir, "minshawi_summary.json"))
    
    # Extract from Abdul Basit
    print("\nProcessing Abdul Basit JSON...")
    abdul_basit_data = load_json_data(ABDUL_BASIT_JSON_PATH)
    if abdul_basit_data:
        abdul_basit_timestamps = extract_timestamps_from_json(abdul_basit_data, "Abdul Basit")
        print(f"Extracted timestamps for {len(abdul_basit_timestamps)} surahs from Abdul Basit")
        
        # Save Abdul Basit timestamps
        save_timestamps_as_json(abdul_basit_timestamps, os.path.join(output_dir, "abdul_basit_timestamps.json"))
        save_timestamps_as_csv(abdul_basit_timestamps, os.path.join(output_dir, "abdul_basit_timestamps.csv"))
        save_timestamps_by_surah(abdul_basit_timestamps, os.path.join(output_dir, "abdul_basit_by_surah"))
        create_word_level_summary(abdul_basit_timestamps, os.path.join(output_dir, "abdul_basit_summary.json"))
    
    # Extract from Mishary
    print("\nProcessing Mishary JSON...")
    mishary_data = load_json_data(MISHARY_JSON_PATH)
    if mishary_data:
        mishary_timestamps = extract_timestamps_from_json(mishary_data, "Mishary")
        print(f"Extracted timestamps for {len(mishary_timestamps)} surahs from Mishary")
        
        # Save Mishary timestamps
        save_timestamps_as_json(mishary_timestamps, os.path.join(output_dir, "mishary_timestamps.json"))
        save_timestamps_as_csv(mishary_timestamps, os.path.join(output_dir, "mishary_timestamps.csv"))
        save_timestamps_by_surah(mishary_timestamps, os.path.join(output_dir, "mishary_by_surah"))
        create_word_level_summary(mishary_timestamps, os.path.join(output_dir, "mishary_summary.json"))
    
    # Extract from Maher Al-Mu'aiqly
    print("\nProcessing Maher Al-Mu'aiqly JSON...")
    maher_data = load_json_data(MAHER_JSON_PATH)
    if maher_data:
        maher_timestamps = extract_timestamps_from_json(maher_data, "Maher Al-Mu'aiqly")
        print(f"Extracted timestamps for {len(maher_timestamps)} surahs from Maher Al-Mu'aiqly")
        
        # Save Maher Al-Mu'aiqly timestamps
        save_timestamps_as_json(maher_timestamps, os.path.join(output_dir, "maher_timestamps.json"))
        save_timestamps_as_csv(maher_timestamps, os.path.join(output_dir, "maher_timestamps.csv"))
        save_timestamps_by_surah(maher_timestamps, os.path.join(output_dir, "maher_by_surah"))
        create_word_level_summary(maher_timestamps, os.path.join(output_dir, "maher_summary.json"))
    
    # Extract from Yasser Al-Dosari
    print("\nProcessing Yasser Al-Dosari JSON...")
    yasser_data = load_json_data(YASSER_JSON_PATH)
    if yasser_data:
        yasser_timestamps = extract_timestamps_from_json(yasser_data, "Yasser Al-Dosari")
        print(f"Extracted timestamps for {len(yasser_timestamps)} surahs from Yasser Al-Dosari")
        
        # Save Yasser Al-Dosari timestamps
        save_timestamps_as_json(yasser_timestamps, os.path.join(output_dir, "yasser_timestamps.json"))
        save_timestamps_as_csv(yasser_timestamps, os.path.join(output_dir, "yasser_timestamps.csv"))
        save_timestamps_by_surah(yasser_timestamps, os.path.join(output_dir, "yasser_by_surah"))
        create_word_level_summary(yasser_timestamps, os.path.join(output_dir, "yasser_summary.json"))
    
    # Extract from Saud Al-Shuraim
    print("\nProcessing Saud Al-Shuraim JSON...")
    shuraim_data = load_json_data(SHURAIM_JSON_PATH)
    if shuraim_data:
        shuraim_timestamps = extract_timestamps_from_json(shuraim_data, "Saud Al-Shuraim")
        print(f"Extracted timestamps for {len(shuraim_timestamps)} surahs from Saud Al-Shuraim")
        
        # Save Saud Al-Shuraim timestamps
        save_timestamps_as_json(shuraim_timestamps, os.path.join(output_dir, "shuraim_timestamps.json"))
        save_timestamps_as_csv(shuraim_timestamps, os.path.join(output_dir, "shuraim_timestamps.csv"))
        save_timestamps_by_surah(shuraim_timestamps, os.path.join(output_dir, "shuraim_by_surah"))
        create_word_level_summary(shuraim_timestamps, os.path.join(output_dir, "shuraim_summary.json"))
    
    # Create combined dataset
    if husary_data and minshawi_data and abdul_basit_data and mishary_data and maher_data and yasser_data and shuraim_data:
        print("\nCreating combined dataset...")
        combined_timestamps = {}
        
        for surah_num in SURAH_NUMBERS_TO_EXTRACT:
            combined_timestamps[surah_num] = {
                "husary": husary_timestamps.get(surah_num, {}),
                "minshawi": minshawi_timestamps.get(surah_num, {}),
                "abdul_basit": abdul_basit_timestamps.get(surah_num, {}),
                "mishary": mishary_timestamps.get(surah_num, {}),
                "maher": maher_timestamps.get(surah_num, {}),
                "yasser": yasser_timestamps.get(surah_num, {}),
                "shuraim": shuraim_timestamps.get(surah_num, {})
            }
        
        save_timestamps_as_json(combined_timestamps, os.path.join(output_dir, "combined_timestamps.json"))
        print(f"Saved combined timestamps to: {os.path.join(output_dir, 'combined_timestamps.json')}")
    
    print(f"\nExtraction complete! All files saved to: {output_dir}")
    print("\nFiles created:")
    print("- JSON files with full timestamp data")
    print("- CSV files for easy analysis in Excel/Google Sheets")
    print("- Individual surah files for focused work")
    print("- Summary files with statistics")
    print("\nYou can now use these files for:")
    print("- Audio annotation and synchronization")
    print("- Tajweed rule analysis")
    print("- Word-level feature extraction")
    print("- Recitation comparison studies")

if __name__ == "__main__":
    main() 