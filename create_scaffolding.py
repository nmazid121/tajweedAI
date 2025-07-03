import json
import os

def create_scaffolding(input_json_path, output_json_path, target_surahs):
    """
    Creates a scaffolding JSON file for Tajweed rule annotation.

    This function reads a JSON file containing word-level timestamps for Quranic
    recitation, and for a specific set of surahs, it generates a new JSON 
    structure. This new structure is designed to be manually filled in with
    character-level Tajweed rules.

    The output JSON is organized by surah and ayah number. Each ayah contains a
    list of words, and each word is broken down into its constituent characters.
    Each character object has a placeholder "to be filled" for the Tajweed rule.

    Args:
        input_json_path (str): The path to the source JSON file containing
                               word timestamps and text.
        output_json_path (str): The path where the generated scaffolding
                                JSON file will be saved.
        target_surahs (list of int): A list of surah numbers to process.
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_json_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_json_path}")
        return

    scaffolding = {}

    for segment in data:
        surah_num = int(segment['surah'])
        if surah_num not in target_surahs:
            continue

        ayah_num = int(segment['ayah'])
        word_text = segment['text']
        
        # Word text from the source json is 'word_1', 'word_2', etc.
        # We need the actual arabic text. The 'text' field in the segment IS the word.
        # The source JSON is a list of dictionaries, where each dict is a word.
        # So 'word_text' is just 'text'
        
        if surah_num not in scaffolding:
            scaffolding[surah_num] = {}

        if ayah_num not in scaffolding[surah_num]:
            scaffolding[surah_num][ayah_num] = {"words": []}

        word_obj = {
            "word_text": word_text,
            "characters": []
        }

        for char in word_text:
            char_obj = {
                "char": char,
                "tajweed_rule": "to be filled"
            }
            word_obj["characters"].append(char_obj)
        
        scaffolding[surah_num][ayah_num]["words"].append(word_obj)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_json_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(scaffolding, f, ensure_ascii=False, indent=4)

    print(f"Scaffolding file created at: {output_json_path}")
    # Also print the structure for a small part to verify
    if 1 in scaffolding and 1 in scaffolding[1] and scaffolding[1][1]["words"]:
         print("\\n--- Example from Surah 1, Ayah 1 ---")
         print(json.dumps(scaffolding[1][1]["words"][0], ensure_ascii=False, indent=4))
         print("------------------------------------")


if __name__ == '__main__':
    # Using Mishary's timestamp file as the source for the text
    INPUT_FILE = os.path.join('download_script', 'extracted_timestamps', 'mishary_timestamps.json')
    
    # Define the output directory and file path
    OUTPUT_DIR = 'tajweed_annotation'
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'tajweed_scaffolding.json')

    # Surahs to be processed
    TARGET_SURAHS = [1, 109, 110, 111, 112, 113, 114]

    create_scaffolding(INPUT_FILE, OUTPUT_FILE, TARGET_SURAHS) 