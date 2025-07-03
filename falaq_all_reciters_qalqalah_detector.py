import json
import re
import os
from datetime import datetime

# Configuration
BASE_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\download_script'
TIMESTAMPS_BASE_PATH = os.path.join(BASE_PATH, 'extracted_timestamps')

# Define all reciters and their folder names
RECITERS = {
    'husary': {
        'folder': 'downloaded_quran_audio_direct',
        'timestamps': 'husary_by_surah',
        'display_name': 'Mahmoud Khalil Al-Husary'
    },
    'shuraim': {
        'folder': 'downloaded_quran_audio_direct_shuraim',
        'timestamps': 'shuraim_by_surah',
        'display_name': 'Saud Al-Shuraim'
    },
    'yasser': {
        'folder': 'downloaded_quran_audio_direct_yasser',
        'timestamps': 'yasser_by_surah',
        'display_name': 'Yasser Al-Dossary'
    },
    'maher': {
        'folder': 'downloaded_quran_audio_direct_maher',
        'timestamps': 'maher_by_surah',
        'display_name': 'Maher Al-Mueaqly'
    },
    'mishary': {
        'folder': 'downloaded_quran_audio_direct_mishary',
        'timestamps': 'mishary_by_surah',
        'display_name': 'Mishary Rashid Alafasy'
    },
    'abdul_basit': {
        'folder': 'downloaded_quran_audio_direct_abdul_basit',
        'timestamps': 'abdul_basit_by_surah',
        'display_name': 'Abdul Basit Abdul Samad'
    },
    'minshawi': {
        'folder': 'downloaded_quran_audio_direct_minshawi',
        'timestamps': 'minshawi_by_surah',
        'display_name': 'Mohammed Siddiq Al-Minshawi'
    }
}

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

def load_timestamps(reciter_key):
    """Load the timestamps file for a specific reciter."""
    reciter_info = RECITERS[reciter_key]
    timestamps_path = os.path.join(TIMESTAMPS_BASE_PATH, reciter_info['timestamps'], '113_Al-Falaq_timestamps.json')
    
    try:
        with open(timestamps_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Timestamps file not found for {reciter_info['display_name']} at {timestamps_path}")
        return None
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {timestamps_path}")
        return None
    except Exception as e:
        print(f"Warning: Error loading timestamps for {reciter_info['display_name']}: {e}")
        return None

def get_local_audio_path(reciter_key, ayah_number):
    """Get the local path to the audio file for a given reciter and ayah."""
    reciter_info = RECITERS[reciter_key]
    audio_base_path = os.path.join(BASE_PATH, reciter_info['folder'], '113_Al-Falaq')
    audio_filename = f"Ayah_{ayah_number:03d}.mp3"
    audio_path = os.path.join(audio_base_path, audio_filename)
    
    # Check if file exists
    if os.path.exists(audio_path):
        return audio_path
    else:
        print(f"Warning: Audio file not found for {reciter_info['display_name']} at {audio_path}")
        return None

def check_reciter_availability(reciter_key):
    """Check if a reciter has both audio files and timestamps available."""
    reciter_info = RECITERS[reciter_key]
    
    # Check audio files
    audio_base_path = os.path.join(BASE_PATH, reciter_info['folder'], '113_Al-Falaq')
    if not os.path.exists(audio_base_path):
        return False
    
    # Check if all 5 ayahs exist
    for ayah_num in range(1, 6):
        audio_path = os.path.join(audio_base_path, f"Ayah_{ayah_num:03d}.mp3")
        if not os.path.exists(audio_path):
            return False
    
    # Check timestamps
    timestamps_path = os.path.join(TIMESTAMPS_BASE_PATH, reciter_info['timestamps'], '113_Al-Falaq_timestamps.json')
    if not os.path.exists(timestamps_path):
        return False
    
    return True

def create_reciter_annotations(reciter_key):
    """
    Create annotated dataset for a specific reciter.
    """
    reciter_info = RECITERS[reciter_key]
    
    # Load timestamps
    timestamps_data = load_timestamps(reciter_key)
    if not timestamps_data:
        return None
    
    # Create the annotated dataset
    annotations = {
        "metadata": {
            "surah_name": "Al-Falaq",
            "surah_number": 113,
            "total_ayahs": 5,
            "created_date": datetime.now().isoformat(),
            "reciter": reciter_info['display_name'],
            "reciter_key": reciter_key,
            "description": f"Tajweed annotation dataset for Surah Al-Falaq with {reciter_info['display_name']} recordings",
            "audio_source": f"Local {reciter_info['display_name']} recordings",
            "timestamps_source": "Extracted from Tarteel API",
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
        
        if ayah_key not in timestamps_data["ayahs"]:
            continue
        
        ayah_timestamps = timestamps_data["ayahs"][ayah_key]
        arabic_text = FALAQ_TEXT[ayah_num]
        
        # Get local audio path
        local_audio_path = get_local_audio_path(reciter_key, ayah_num)
        
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
            "audio_url": ayah_timestamps.get("audio_url", ""),  # Keep original URL for reference
            "local_audio_path": local_audio_path,
            "arabic_text": arabic_text,
            "segments": ayah_timestamps.get("segments", []),
            "reciter": reciter_info['display_name'],
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

def save_annotations(annotations, reciter_key):
    """Save the annotations to a JSON file."""
    output_file = f'falaq_tajweed_annotations_{reciter_key}.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, ensure_ascii=False, indent=2)
        print(f"✅ Annotations saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error saving annotations for {reciter_key}: {e}")
        return None

def print_reciter_summary(annotations, reciter_key):
    """Print a summary for a specific reciter."""
    if not annotations:
        return
    
    reciter_info = RECITERS[reciter_key]
    print(f"\n🎵 {reciter_info['display_name']} ({reciter_key.upper()})")
    print("-" * 50)
    
    total_qalqalah_words = 0
    total_qalqalah_occurrences = 0
    total_kubra = 0
    total_sughra = 0
    
    for ayah_num in range(1, 6):
        ayah_key = str(ayah_num)
        if ayah_key not in annotations["ayahs"]:
            continue
        
        ayah = annotations["ayahs"][ayah_key]
        qalqalah_words = ayah['qalqalah_summary']['words_with_qalqalah']
        
        if qalqalah_words:
            print(f"  Ayah {ayah_num}: {', '.join(qalqalah_words)} (Kubra: {ayah['qalqalah_summary']['qalqalah_kubra_count']})")
        else:
            print(f"  Ayah {ayah_num}: No Qalqalah")
        
        total_qalqalah_words += ayah['total_qalqalah_words']
        total_qalqalah_occurrences += ayah['qalqalah_summary']['total_occurrences']
        total_kubra += ayah['qalqalah_summary']['qalqalah_kubra_count']
        total_sughra += ayah['qalqalah_summary']['qalqalah_sughra_count']
    
    print(f"  📊 Total: {total_kubra} Kubra, {total_sughra} Sughra")
    return {
        'reciter': reciter_info['display_name'],
        'key': reciter_key,
        'total_kubra': total_kubra,
        'total_sughra': total_sughra,
        'total_occurrences': total_qalqalah_occurrences
    }

def main():
    """
    Main function to process all reciters for Surah Al-Falaq.
    """
    print("🎯 PROCESSING ALL RECITERS FOR SURAH AL-FALAQ QALQALAH DETECTION")
    print("=" * 80)
    
    # Check availability for each reciter
    available_reciters = []
    for reciter_key in RECITERS.keys():
        if check_reciter_availability(reciter_key):
            available_reciters.append(reciter_key)
            print(f"✅ {RECITERS[reciter_key]['display_name']} - Available")
        else:
            print(f"❌ {RECITERS[reciter_key]['display_name']} - Not available")
    
    if not available_reciters:
        print("\n❌ No reciters available. Please check your audio files and timestamps.")
        return
    
    print(f"\n🎵 Processing {len(available_reciters)} available reciters...")
    
    # Process each available reciter
    results = []
    for reciter_key in available_reciters:
        print(f"\n🔄 Processing {RECITERS[reciter_key]['display_name']}...")
        
        # Create annotations
        annotations = create_reciter_annotations(reciter_key)
        
        if annotations:
            # Save annotations
            output_file = save_annotations(annotations, reciter_key)
            
            # Print summary
            result = print_reciter_summary(annotations, reciter_key)
            if result:
                results.append(result)
        else:
            print(f"❌ Failed to create annotations for {RECITERS[reciter_key]['display_name']}")
    
    # Print overall summary
    print(f"\n" + "=" * 80)
    print("📊 OVERALL SUMMARY")
    print("=" * 80)
    
    total_reciters = len(results)
    total_kubra = sum(r['total_kubra'] for r in results)
    total_sughra = sum(r['total_sughra'] for r in results)
    
    print(f"Total reciters processed: {total_reciters}")
    print(f"Total Qalqalah Kubra instances: {total_kubra}")
    print(f"Total Qalqalah Sughra instances: {total_sughra}")
    print(f"Average Qalqalah Kubra per reciter: {total_kubra/total_reciters:.1f}")
    
    print(f"\n📁 Generated files:")
    for result in results:
        print(f"   - falaq_tajweed_annotations_{result['key']}.json")
    
    print(f"\n🎯 RECOMMENDATION: You now have {total_kubra} Qalqalah Kubra instances")
    print(f"   across {total_reciters} reciters for robust acoustic signature analysis!")
    print("=" * 80)

if __name__ == "__main__":
    main() 