import json
import os
import shutil
from pathlib import Path

def extract_last_word_segments():
    """
    Extract the last word segment from each ayah in the selected JSONs
    and organize them for CTC forced aligner input.
    """
    
    # Define paths
    selected_ayahs_dir = Path("extracted_timestamps/surah_falaq_inshiqaq/selected_ayahs")
    ctc_input_dir = Path("extracted_timestamps/surah_falaq_inshiqaq/selected_ayahs/ctc-forced-aligner-inputs")
    
    # Create CTC input directory
    ctc_input_dir.mkdir(exist_ok=True)
    
    # Store all last word segments
    all_last_segments = []
    
    # Process each JSON file
    for json_file in selected_ayahs_dir.glob("*_selected.json"):
        print(f"Processing: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            surah_number = data['surah_number']
            surah_name = data['surah_name']
            
            # Extract reciter name from filename
            # Format: reciter-name_84_Al-Inshiqaq_selected.json
            filename_parts = json_file.stem.split('_')
            reciter_name = '_'.join(filename_parts[:-3])  # Everything before the surah number
            
            # Process each ayah
            for ayah_num, ayah_data in data['ayahs'].items():
                ayah_number = int(ayah_num)
                segments = ayah_data['segments']
                
                if not segments:
                    print(f"  Warning: No segments found for {reciter_name} - Surah {surah_number}:{ayah_number}")
                    continue
                
                # Get the last segment (last word)
                last_segment = segments[-1]
                segment_num, start_time, end_time = last_segment
                
                # Create entry for this last word segment
                segment_entry = {
                    'reciter': reciter_name,
                    'surah_number': surah_number,
                    'surah_name': surah_name,
                    'ayah_number': ayah_number,
                    'audio_url': ayah_data['audio_url'],
                    'last_word_segment': {
                        'segment_number': segment_num,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': end_time - start_time
                    },
                    'full_ayah_segments': segments  # Keep all segments for reference
                }
                
                all_last_segments.append(segment_entry)
                
                print(f"  Extracted last word from {reciter_name} - Surah {surah_number}:{ayah_number} "
                      f"(segment {segment_num}: {start_time}-{end_time}ms)")
        
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
            continue
    
    # Save all last word segments to a comprehensive JSON
    comprehensive_file = ctc_input_dir / "all_last_word_segments.json"
    with open(comprehensive_file, 'w', encoding='utf-8') as f:
        json.dump(all_last_segments, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved comprehensive data to: {comprehensive_file}")
    
    # Create a simplified CSV for easy processing
    csv_file = ctc_input_dir / "last_word_segments.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("reciter,surah_number,surah_name,ayah_number,audio_url,segment_number,start_time,end_time,duration\n")
        for entry in all_last_segments:
            seg = entry['last_word_segment']
            f.write(f"{entry['reciter']},{entry['surah_number']},{entry['surah_name']},"
                   f"{entry['ayah_number']},{entry['audio_url']},{seg['segment_number']},"
                   f"{seg['start_time']},{seg['end_time']},{seg['duration']}\n")
    
    print(f"Saved CSV data to: {csv_file}")
    
    # Create per-reciter JSONs for easier processing
    reciters = {}
    for entry in all_last_segments:
        reciter = entry['reciter']
        if reciter not in reciters:
            reciters[reciter] = []
        reciters[reciter].append(entry)
    
    for reciter, segments in reciters.items():
        reciter_file = ctc_input_dir / f"{reciter}_last_word_segments.json"
        with open(reciter_file, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        print(f"Saved {reciter} data to: {reciter_file}")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total last word segments extracted: {len(all_last_segments)}")
    print(f"Reciters processed: {len(reciters)}")
    print(f"Files created in: {ctc_input_dir}")
    print(f"  - all_last_word_segments.json (comprehensive data)")
    print(f"  - last_word_segments.csv (simplified format)")
    print(f"  - {len(reciters)} per-reciter JSON files")
    
    return all_last_segments

if __name__ == "__main__":
    print("Extracting last word segments for CTC forced aligner...")
    print("=" * 60)
    segments = extract_last_word_segments()
    print("\nReady for CTC forced aligner processing!") 