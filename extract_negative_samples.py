import json
import os
from pydub import AudioSegment
import glob

def extract_negative_samples():
    """Extract high-quality negative samples from words that don't contain Qalqalah"""
    
    # Create output directory
    output_dir = "negative_samples"
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all annotation files
    annotation_files = glob.glob("falaq_tajweed_annotations_*.json")
    
    negative_count = 0
    
    for annotation_file in annotation_files:
        # Get reciter name from filename
        reciter = annotation_file.replace("falaq_tajweed_annotations_", "").replace(".json", "")
        
        print(f"Processing {reciter}...")
        
        # Create reciter directory
        reciter_dir = os.path.join(output_dir, reciter)
        os.makedirs(reciter_dir, exist_ok=True)
        
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Process each ayah
        for ayah_num, ayah_data in data['ayahs'].items():
            print(f"  Processing Ayah {ayah_num}...")
            
            # Find which word has Qalqalah
            qalqalah_word_index = None
            for word in ayah_data['words']:
                if word.get('has_qalqalah', False):
                    qalqalah_word_index = word['word_index']
                    break
            
            # Load audio file
            audio_path = ayah_data['local_audio_path']
            if not os.path.exists(audio_path):
                print(f"    Audio file not found: {audio_path}")
                continue
                
            audio = AudioSegment.from_mp3(audio_path)
            
            # Extract non-Qalqalah words with quality filtering
            for i, segment in enumerate(ayah_data['segments']):
                word_index = segment[0]
                start_time = segment[1]
                end_time = segment[2]
                duration = end_time - start_time
                
                # Skip if this word contains Qalqalah
                if word_index == qalqalah_word_index:
                    continue
                
                # QUALITY FILTER: Only keep words with reasonable duration
                if duration < 200:  # Too short, skip
                    print(f"    Skipping short word: {duration}ms")
                    continue
                elif duration > 2000:  # Too long, might be multiple words
                    print(f"    Skipping long word: {duration}ms")
                    continue
                
                # Extract word audio with small buffer for context
                buffer_ms = 50  # Add 50ms buffer on each side
                buffered_start = max(0, start_time - buffer_ms)
                buffered_end = min(len(audio), end_time + buffer_ms)
                
                word_audio = audio[buffered_start:buffered_end]
                
                # Get word text (if available)
                word_text = "unknown"
                for word in ayah_data['words']:
                    if word['word_index'] == word_index:
                        word_text = word['word_text']
                        break
                
                # Additional filter: Skip very common short words
                skip_words = ['مِن', 'فِي', 'مَا', 'إِذَا']
                if word_text in skip_words:
                    print(f"    Skipping common short word: {word_text}")
                    continue
                
                # Save negative sample
                filename = f"negative_ayah{ayah_num}_word{word_index}_{word_text}.mp3"
                output_path = os.path.join(reciter_dir, filename)
                word_audio.export(output_path, format="mp3")
                
                # Create annotation
                annotation = {
                    "ayah": int(ayah_num),
                    "word": word_text,
                    "word_index": word_index,
                    "has_qalqalah": False,
                    "reciter": reciter,
                    "timing": {
                        "original_start": start_time,
                        "original_end": end_time,
                        "original_duration_ms": duration,
                        "buffered_start": buffered_start,
                        "buffered_end": buffered_end,
                        "final_duration_ms": len(word_audio)
                    },
                    "audio_file": filename,
                    "quality": "filtered"
                }
                
                annotation_path = os.path.join(reciter_dir, filename.replace(".mp3", ".json"))
                with open(annotation_path, 'w', encoding='utf-8') as f:
                    json.dump(annotation, f, indent=2, ensure_ascii=False)
                
                negative_count += 1
                print(f"    Saved: {filename} ({len(word_audio)}ms)")
    
    print(f"\nTotal high-quality negative samples extracted: {negative_count}")
    print(f"Samples saved in: {output_dir}/")
    
    return negative_count

def analyze_dataset():
    """Analyze the complete dataset (positive + negative)"""
    
    # Count positive samples
    positive_count = 0
    positive_durations = []
    for letter in ['ق', 'ب', 'د']:
        letter_dir = f"qalqalah_samples/{letter}"
        if os.path.exists(letter_dir):
            for reciter in os.listdir(letter_dir):
                reciter_path = os.path.join(letter_dir, reciter)
                if os.path.isdir(reciter_path):
                    for ayah in os.listdir(reciter_path):
                        ayah_path = os.path.join(reciter_path, ayah)
                        if os.path.isdir(ayah_path):
                            # Check if it has audio file
                            audio_files = [f for f in os.listdir(ayah_path) if f.endswith('.mp3')]
                            if audio_files:
                                positive_count += 1
                                # Try to get duration from annotation
                                json_files = [f for f in os.listdir(ayah_path) if f.endswith('.json')]
                                if json_files:
                                    json_path = os.path.join(ayah_path, json_files[0])
                                    with open(json_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                        duration = data['timing']['qalqalah_duration_ms']
                                        positive_durations.append(duration)
    
    # Count negative samples
    negative_count = 0
    negative_durations = []
    negative_dir = "negative_samples"
    if os.path.exists(negative_dir):
        for reciter in os.listdir(negative_dir):
            reciter_path = os.path.join(negative_dir, reciter)
            if os.path.isdir(reciter_path):
                json_files = [f for f in os.listdir(reciter_path) if f.endswith('.json')]
                negative_count += len(json_files)
                
                # Get durations
                for json_file in json_files:
                    json_path = os.path.join(reciter_path, json_file)
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        duration = data['timing']['final_duration_ms']
                        negative_durations.append(duration)
    
    print(f"\n=== DATASET ANALYSIS ===")
    print(f"Positive samples (Qalqalah): {positive_count}")
    print(f"Negative samples (Non-Qalqalah): {negative_count}")
    print(f"Total samples: {positive_count + negative_count}")
    
    if negative_count > 0:
        print(f"Positive:Negative ratio: 1:{negative_count/positive_count:.1f}")
        
        # Duration analysis
        if positive_durations:
            avg_pos_duration = sum(positive_durations) / len(positive_durations)
            print(f"Average positive duration: {avg_pos_duration:.0f}ms")
            
        if negative_durations:
            avg_neg_duration = sum(negative_durations) / len(negative_durations)
            print(f"Average negative duration: {avg_neg_duration:.0f}ms")
            
        # Quality assessment
        if negative_count > positive_count * 3:
            print("\n⚠️  WARNING: Too many negative samples. Consider reducing.")
        elif negative_count < positive_count * 0.5:
            print("\n⚠️  WARNING: Too few negative samples. Consider adding more.")
        else:
            print("\n✅ Good balance of positive and negative samples!")
    else:
        print("No negative samples found.")

if __name__ == "__main__":
    print("Extracting high-quality negative samples...")
    extract_negative_samples()
    print("\nAnalyzing complete dataset...")
    analyze_dataset() 