import shutil
import os
from pathlib import Path

def prepare_qalqalah_segments_for_training():
    """
    Copy extracted Qalqalah segments to the falaq_word_approach folder
    for model training
    """
    
    # Define paths
    source_dir = Path("extracted_timestamps/surah_falaq_inshiqaq/selected_ayahs/ctc-forced-aligner-inputs/extracted_qalqalah_segments_simple")
    target_dir = Path("3_falaq_word_approach/positive_samples_qalqalah_kubra")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Count files
    wav_files = list(source_dir.glob("*.wav"))
    print(f"Found {len(wav_files)} Qalqalah audio segments")
    
    # Copy files
    copied_count = 0
    for wav_file in wav_files:
        try:
            # Copy to target directory
            shutil.copy2(wav_file, target_dir / wav_file.name)
            copied_count += 1
            print(f"Copied: {wav_file.name}")
        except Exception as e:
            print(f"Error copying {wav_file.name}: {e}")
    
    print(f"\n=== PREPARATION COMPLETE ===")
    print(f"Successfully copied {copied_count} Qalqalah segments")
    print(f"Target directory: {target_dir}")
    
    # Create a summary file
    summary_file = target_dir / "qalqalah_segments_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("Qalqalah Kubra Audio Segments for Model Training\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total segments: {copied_count}\n")
        f.write(f"Source: Extracted from last words of ayahs ending with Qaf (ق)\n")
        f.write(f"Reciters: 15 different reciters\n")
        f.write(f"Surahs: Al-Falaq (113:1-2) and Al-Inshiqaq (84:16-19)\n\n")
        f.write("File naming convention:\n")
        f.write("reciter_sXXXaYYY_qalqalah.wav\n")
        f.write("Where XXX = surah number, YYY = ayah number\n\n")
        f.write("These segments contain the Qalqalah Kubra sound (aq)\n")
        f.write("from the last word of each ayah, which ends with Qaf.\n")
    
    print(f"Summary file created: {summary_file}")
    
    return copied_count

if __name__ == "__main__":
    print("Preparing Qalqalah segments for model training...")
    print("=" * 60)
    count = prepare_qalqalah_segments_for_training()
    print(f"\nReady for model training with {count} Qalqalah Kubra samples!") 