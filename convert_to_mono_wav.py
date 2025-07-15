import os
import glob
from pydub import AudioSegment
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_mp3_to_mono_wav(input_path, output_path, sample_rate=16000):
    """
    Convert MP3 file to mono WAV format
    
    Args:
        input_path (str): Path to input MP3 file
        output_path (str): Path to output WAV file
        sample_rate (int): Target sample rate (default 16000 for STT models)
    """
    try:
        # Load the MP3 file
        audio = AudioSegment.from_mp3(input_path)
        
        # Convert to mono
        audio = audio.set_channels(1)
        
        # Set sample rate
        audio = audio.set_frame_rate(sample_rate)
        
        # Export as WAV
        audio.export(output_path, format="wav")
        
        logger.info(f"Converted: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error converting {input_path}: {str(e)}")
        return False

def process_directory(input_dir, output_dir, sample_rate=16000):
    """
    Process all MP3 files in a directory and convert them to mono WAV
    
    Args:
        input_dir (str): Input directory containing MP3 files
        output_dir (str): Output directory for WAV files
        sample_rate (int): Target sample rate
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all MP3 files recursively
    mp3_files = glob.glob(os.path.join(input_dir, "**/*.mp3"), recursive=True)
    
    if not mp3_files:
        logger.warning(f"No MP3 files found in {input_dir}")
        return
    
    logger.info(f"Found {len(mp3_files)} MP3 files in {input_dir}")
    
    success_count = 0
    error_count = 0
    
    for mp3_file in mp3_files:
        # Get relative path from input directory
        rel_path = os.path.relpath(mp3_file, input_dir)
        
        # Change extension from .mp3 to .wav
        wav_filename = os.path.splitext(rel_path)[0] + ".wav"
        
        # Create output path
        wav_file = os.path.join(output_dir, wav_filename)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(wav_file), exist_ok=True)
        
        # Convert the file
        if convert_mp3_to_mono_wav(mp3_file, wav_file, sample_rate):
            success_count += 1
        else:
            error_count += 1
    
    logger.info(f"Conversion complete for {input_dir}:")
    logger.info(f"  Success: {success_count}")
    logger.info(f"  Errors: {error_count}")

def main():
    """Main function to convert all samples to mono WAV"""
    
    # Define paths
    base_dir = "falaq_word_approach"
    positive_samples_dir = os.path.join(base_dir, "positive_samples")
    negative_samples_dir = os.path.join(base_dir, "negative_samples")
    
    # Output directories
    positive_wav_dir = os.path.join(base_dir, "positive_samples_wav")
    negative_wav_dir = os.path.join(base_dir, "negative_samples_wav")
    
    logger.info("Starting MP3 to mono WAV conversion...")
    
    # Convert positive samples
    if os.path.exists(positive_samples_dir):
        logger.info("Processing positive samples...")
        process_directory(positive_samples_dir, positive_wav_dir)
    else:
        logger.warning(f"Positive samples directory not found: {positive_samples_dir}")
    
    # Convert negative samples
    if os.path.exists(negative_samples_dir):
        logger.info("Processing negative samples...")
        process_directory(negative_samples_dir, negative_wav_dir)
    else:
        logger.warning(f"Negative samples directory not found: {negative_samples_dir}")
    
    logger.info("Conversion process completed!")

if __name__ == "__main__":
    main() 