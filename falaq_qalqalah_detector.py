import json
import re
from datetime import datetime

# Configuration
JSON_FILE_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\download_script\ayah-recitation-mahmoud-khalil-al-husary-murattal-hafs-957.json'
OUTPUT_FILE = 'falaq_tajweed_annotations.json'

# Surah Al-Falaq Arabic text (5 ayahs)
FALAQ_TEXT = {
    1: "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
    2: "مِن شَرِّ مَا خَلَقَ",
    3: "وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ",
    4: "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ",
    5: "وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ"
}

# Qalqalah letters: ق ط ب ج د
QALQALAH_LETTERS = ['ق', 'ط', 'ب', 'ج', 'د']

def detect_qalqalah_strict(ayah_text, ayah_number):
    """
    Detect Qalqalah strictly according to Tajweed rules.
    Focus on Qalqalah Kubra at end-of-ayah stopping.
    Avoid false positives from Tanween letters.
    """
    qalqalah_instances = []
    
    # Split text into words
    words = ayah_text.split()
    
    # Check the last word of the ayah for Qalqalah Kubra (stopping position)
    last_word = words[-1]
    
    # Find the LAST Qalqalah letter in the last word (this is what becomes sakin when stopping)
    last_qalqalah_position = -1
    last_qalqalah_letter = None
    
    for i, char in enumerate(last_word):
        if char in QALQALAH_LETTERS:
            last_qalqalah_position = i
            last_qalqalah_letter = char
    
    # Only add Qalqalah Kubra for the last Qalqalah letter in the word
    if last_qalqalah_position >= 0:
        qalqalah_instances.append({
            'word': last_word,
            'word_position': len(words),  # Last word
            'letter': last_qalqalah_letter,
            'letter_position': last_qalqalah_position,
            'type': 'Qalqalah_Kubra',
            'reason': f'Qalqalah letter {last_qalqalah_letter} at end of ayah {ayah_number} (stopping position - becomes sakin)',
            'ayah_end': True,
            'confidence': 'High'
        })
    
    # Check for Qalqalah Sughra within words (only for letters with actual sukoon)
    for word_index, word in enumerate(words, 1):
        for i, char in enumerate(word):
            if char in QALQALAH_LETTERS:
                # Only consider if it's not the last word (already handled above)
                if word_index < len(words):
                    # Check if the letter has sukoon (ْ) or is followed by another consonant
                    if i < len(word) - 1:
                        next_char = word[i + 1]
                        # Check for actual sukoon (ْ) or consonant (not vowel marks)
                        if next_char == 'ْ' or next_char not in ['َ', 'ِ', 'ُ', 'ّ', 'ً', 'ٍ', 'ٌ']:
                            qalqalah_instances.append({
                                'word': word,
                                'word_position': word_index,
                                'letter': char,
                                'letter_position': i,
                                'type': 'Qalqalah_Sughra',
                                'reason': f'Qalqalah letter {char} with sukoon within word',
                                'ayah_end': False,
                                'confidence': 'Medium'
                            })
    
    return qalqalah_instances

def extract_falaq_data(json_file_path):
    """
    Extract Surah Al-Falaq data from the JSON file.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        falaq_data = {}
        
        # Extract ayahs 113:1 to 113:5
        for ayah_num in range(1, 6):
            key = f"113:{ayah_num}"
            if key in data:
                falaq_data[str(ayah_num)] = data[key]
        
        return falaq_data
    
    except FileNotFoundError:
        print(f"Error: JSON file not found at '{json_file_path}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def create_falaq_annotations():
    """
    Create annotated dataset for Surah Al-Falaq with strict Qalqalah detection.
    """
    # Extract data from JSON
    falaq_data = extract_falaq_data(JSON_FILE_PATH)
    
    if not falaq_data:
        return None
    
    # Create the annotated dataset
    annotations = {
        "metadata": {
            "surah_name": "Al-Falaq",
            "surah_number": 113,
            "total_ayahs": 5,
            "created_date": datetime.now().isoformat(),
            "description": "Tajweed annotation dataset for Surah Al-Falaq with strict Qalqalah detection",
            "qalqalah_letters": QALQALAH_LETTERS,
            "qalqalah_rules": {
                "definition": "Qalqalah is a bouncing/echoing sound produced when pronouncing certain letters",
                "letters": "ق ط ب ج د",
                "qalqalah_kubra": "Strong Qalqalah - occurs when stopping at the end of an ayah on a Qalqalah letter (becomes sakin)",
                "qalqalah_sughra": "Light Qalqalah - occurs when a Qalqalah letter has actual sukoon within a word",
                "strict_conditions": [
                    "Letter must have sukoon (ْ) or become sakin due to stopping",
                    "Tanween (ً ٍ ٌ) does NOT count as sukoon for Qalqalah",
                    "Qalqalah Kubra is the primary focus for end-of-ayah detection",
                    "Only the last Qalqalah letter in the final word becomes sakin when stopping"
                ],
                "notes": "This detection focuses on Qalqalah Kubra at ayah endings for clear acoustic signature"
            }
        },
        "ayahs": {}
    }
    
    # Process each ayah
    for ayah_num in range(1, 6):
        ayah_key = str(ayah_num)
        
        if ayah_key not in falaq_data:
            continue
        
        ayah_data = falaq_data[ayah_key]
        arabic_text = FALAQ_TEXT[ayah_num]
        
        # Detect Qalqalah with strict logic
        qalqalah_instances = detect_qalqalah_strict(arabic_text, ayah_num)
        
        # Split text into words for annotation
        words = arabic_text.split()
        
        # Process each word
        word_annotations = []
        for word_index, word_text in enumerate(words, 1):
            # Find Qalqalah instances for this word
            word_qalqalah = [inst for inst in qalqalah_instances if inst['word'] == word_text]
            
            # Determine if this word has Qalqalah
            has_qalqalah = len(word_qalqalah) > 0
            tajweed_rules = []
            if has_qalqalah:
                for inst in word_qalqalah:
                    if inst['type'] not in tajweed_rules:
                        tajweed_rules.append(inst['type'])
            
            word_annotation = {
                "word_index": word_index,
                "word_text": word_text,
                "tajweed_rules": tajweed_rules,
                "qalqalah_details": word_qalqalah,
                "has_qalqalah": has_qalqalah,
                "is_end_word": word_index == len(words),
                "notes": f"Qalqalah detected: {', '.join([inst['type'] for inst in word_qalqalah])}" if has_qalqalah else "No Qalqalah detected"
            }
            
            word_annotations.append(word_annotation)
        
        # Create ayah annotation
        ayah_annotation = {
            "surah_number": 113,
            "ayah_number": ayah_num,
            "audio_url": ayah_data.get("audio_url", ""),
            "arabic_text": arabic_text,
            "segments": ayah_data.get("segments", []),
            "words": word_annotations,
            "total_qalqalah_words": sum(1 for word in word_annotations if word["has_qalqalah"]),
            "qalqalah_summary": {
                "total_occurrences": len(qalqalah_instances),
                "words_with_qalqalah": list(set([word["word_text"] for word in word_annotations if word["has_qalqalah"]])),
                "qalqalah_kubra_count": len([inst for inst in qalqalah_instances if inst['type'] == 'Qalqalah_Kubra']),
                "qalqalah_sughra_count": len([inst for inst in qalqalah_instances if inst['type'] == 'Qalqalah_Sughra']),
                "primary_targets": list(set([inst['word'] for inst in qalqalah_instances if inst['type'] == 'Qalqalah_Kubra']))
            }
        }
        
        annotations["ayahs"][ayah_key] = ayah_annotation
    
    return annotations

def save_annotations(annotations, output_file):
    """
    Save the annotations to a JSON file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, ensure_ascii=False, indent=2)
        print(f"Annotations saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving annotations: {e}")
        return False

def print_summary(annotations):
    """
    Print a summary of the strict Qalqalah detection results.
    """
    if not annotations:
        return
    
    print("\n" + "="*70)
    print("SURAH AL-FALAQ STRICT QALQALAH DETECTION SUMMARY")
    print("="*70)
    
    print("\n📚 STRICT TAJWEED RULES APPLIED:")
    print("- Qalqalah Kubra: End-of-ayah stopping (primary target)")
    print("- Qalqalah Sughra: Only letters with actual sukoon (ْ)")
    print("- Tanween letters (ً ٍ ٌ) are NOT counted as Qalqalah")
    print("- Only the last Qalqalah letter in final word becomes sakin when stopping")
    
    total_qalqalah_words = 0
    total_qalqalah_occurrences = 0
    total_kubra = 0
    total_sughra = 0
    
    for ayah_num in range(1, 6):
        ayah_key = str(ayah_num)
        if ayah_key not in annotations["ayahs"]:
            continue
        
        ayah = annotations["ayahs"][ayah_key]
        print(f"\n📍 Ayah {ayah_num}: {ayah['arabic_text']}")
        print(f"Audio: {ayah['audio_url']}")
        
        qalqalah_words = ayah['qalqalah_summary']['words_with_qalqalah']
        primary_targets = ayah['qalqalah_summary']['primary_targets']
        
        if qalqalah_words:
            print(f"Words with Qalqalah: {', '.join(qalqalah_words)}")
            print(f"Primary targets (Kubra): {', '.join(primary_targets)}")
            print(f"Total Qalqalah occurrences: {ayah['qalqalah_summary']['total_occurrences']}")
            print(f"  - Qalqalah Kubra: {ayah['qalqalah_summary']['qalqalah_kubra_count']}")
            print(f"  - Qalqalah Sughra: {ayah['qalqalah_summary']['qalqalah_sughra_count']}")
        else:
            print("No Qalqalah detected")
        
        total_qalqalah_words += ayah['total_qalqalah_words']
        total_qalqalah_occurrences += ayah['qalqalah_summary']['total_occurrences']
        total_kubra += ayah['qalqalah_summary']['qalqalah_kubra_count']
        total_sughra += ayah['qalqalah_summary']['qalqalah_sughra_count']
    
    print(f"\n" + "="*70)
    print(f"TOTAL SUMMARY:")
    print(f"Total words with Qalqalah: {total_qalqalah_words}")
    print(f"Total Qalqalah occurrences: {total_qalqalah_occurrences}")
    print(f"  - Qalqalah Kubra (Strong): {total_kubra} - Primary targets for MVP")
    print(f"  - Qalqalah Sughra (Light): {total_sughra}")
    print(f"\n🎯 RECOMMENDATION: Focus on {total_kubra} Qalqalah Kubra instances")
    print(f"   for clear acoustic signature detection in your MVP.")
    print("="*70)

def main():
    """
    Main function to run the strict Qalqalah detection for Surah Al-Falaq.
    """
    print("Analyzing Surah Al-Falaq for strict Qalqalah rules...")
    
    # Create annotations
    annotations = create_falaq_annotations()
    
    if not annotations:
        print("Failed to create annotations.")
        return
    
    # Save to file
    if save_annotations(annotations, OUTPUT_FILE):
        print(f"Successfully created strict annotated dataset for Surah Al-Falaq")
    
    # Print summary
    print_summary(annotations)

if __name__ == "__main__":
    main() 