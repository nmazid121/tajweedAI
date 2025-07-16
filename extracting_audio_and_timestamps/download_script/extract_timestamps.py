import json
import os

RECITERS_DIR = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\all_reciters_json'
OUTPUT_DIR = 'extracted_timestamps'
SURAH_TARGETS = [
    (84, 'Al-Inshiqaq'),
    (113, 'Al-Falaq')
]

def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return None

def extract_surah(json_data, surah_number):
    ayahs = {}
    for key, ayah_info in json_data.items():
        if isinstance(ayah_info, dict) and ayah_info.get('surah_number') == surah_number:
            ayah_number = ayah_info.get('ayah_number')
            ayahs[ayah_number] = ayah_info
    return ayahs

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    reciter_files = [f for f in os.listdir(RECITERS_DIR) if f.endswith('.json') and not f.endswith('.db.json')]
    saved_files = []
    for reciter_file in reciter_files:
        reciter_path = os.path.join(RECITERS_DIR, reciter_file)
        reciter_name = reciter_file.replace('ayah-recitation-', '').replace('.json', '')
        print(f"Processing {reciter_name}...")
        json_data = load_json_data(reciter_path)
        if not json_data:
            continue
        for surah_number, surah_name in SURAH_TARGETS:
            ayahs = extract_surah(json_data, surah_number)
            if ayahs:
                out_data = {
                    'surah_number': surah_number,
                    'surah_name': surah_name,
                    'ayahs': ayahs
                }
                out_file = os.path.join(OUTPUT_DIR, f"{reciter_name}_{surah_number}_{surah_name}.json")
                with open(out_file, 'w', encoding='utf-8') as f:
                    json.dump(out_data, f, indent=2, ensure_ascii=False)
                saved_files.append(out_file)
                print(f"  Saved: {out_file}")
    print("\nSummary of files saved:")
    for f in saved_files:
        print(f"- {f}")
    print("Done!")

if __name__ == "__main__":
    main() 