import json
import re
import os

def find_qalqalah_kubra_qaf_ayahs_in_quran(file_path='quran-metadata-ayah.json'):
    """
    Loads Quranic ayah data from a JSON file and identifies all Ayahs
    in the entire Quran that end with the letter Qaf (ق), which signifies
    Qalqalah Kubra when stopped upon.

    Args:
        file_path (str): The path to your JSON file containing the Quranic data.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              'surah_number', 'ayah_number', and the full 'text' of
              the identified Ayah.
    """
    qalqalah_qaf_ayahs = []

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, file_path)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{json_file_path}': {e}")
        return []

    print(f"Loaded JSON file successfully. Total ayahs: {len(data)}")
    print(f"Searching for ayahs in the entire Quran that end with Qaf (ق)")

    # Iterate through all ayahs in the JSON data
    for ayah_id, ayah_data in data.items():
        try:
            surah_number = ayah_data.get('surah_number')
            ayah_number = ayah_data.get('ayah_number')
            text = ayah_data.get('text', '')

            # Remove ayah number and any trailing spaces/punctuation
            clean_text = re.sub(r'[٠١٢٣٤٥٦٧٨٩\s]+$', '', text.strip())
            if clean_text.endswith('ق'):
                qalqalah_qaf_ayahs.append({
                    'surah_number': surah_number,
                    'ayah_number': ayah_number,
                    'verse_key': ayah_data.get('verse_key', f"{surah_number}:{ayah_number}"),
                    'text': text
                })
        except (KeyError, TypeError) as e:
            print(f"Error processing ayah {ayah_id}: {e}")
            continue

    print(f"\nSummary:")
    print(f"Total ayahs in the Quran that END with Qaf: {len(qalqalah_qaf_ayahs)}")

    # Save only the ayahs that END with Qaf (Qalqalah Kubra Qaf ayahs) to a separate JSON file
    qalqalah_kubra_file = os.path.join(script_dir, 'quran_qalqalah_kubra_qaf.json')
    with open(qalqalah_kubra_file, 'w', encoding='utf-8') as f:
        json.dump(qalqalah_qaf_ayahs, f, ensure_ascii=False, indent=2)
    print(f"Saved all Qalqalah Kubra Qaf ayahs to: {qalqalah_kubra_file}")

    return qalqalah_qaf_ayahs

if __name__ == "__main__":
    print("Searching for Qalqalah Kubra ayahs in the entire Quran...")
    print("(Ayahs ending with the letter Qaf - ق)")
    print("=" * 60)
    qalqalah_ayahs = find_qalqalah_kubra_qaf_ayahs_in_quran()
    if qalqalah_ayahs:
        print(f"\nFound {len(qalqalah_ayahs)} ayahs with Qalqalah Kubra in the Quran:")
        for ayah in qalqalah_ayahs:
            print(f"Surah {ayah['surah_number']}, Ayah {ayah['ayah_number']}: {ayah['text']}")
    else:
        print("\nNo ayahs ending with Qaf (ق) found in the Quran.")
        print("Qalqalah Kubra occurs when stopping on a Qaf letter, but the ayah doesn't necessarily end with it.")