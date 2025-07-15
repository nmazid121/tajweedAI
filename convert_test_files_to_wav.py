import os
import subprocess
import glob
from pathlib import Path

def convert_mp3_to_wav(input_folder):
    """Convert all MP3 files in the folder to WAV format"""
    
    # Find all MP3 files
    mp3_files = glob.glob(os.path.join(input_folder, "*.mp3"))
    
    if not mp3_files:
        print("No MP3 files found to convert.")
        return
    
    print(f"Found {len(mp3_files)} MP3 files to convert:")
    for mp3_file in mp3_files:
        print(f"  - {os.path.basename(mp3_file)}")
    
    # Convert each MP3 file to WAV
    for mp3_file in mp3_files:
        wav_file = mp3_file.replace('.mp3', '.wav')
        
        print(f"\nConverting {os.path.basename(mp3_file)} to WAV...")
        
        try:
            # Use ffmpeg to convert MP3 to WAV with mono channel and 16-bit PCM
            cmd = [
                'ffmpeg', '-i', mp3_file,
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ac', '1',              # Mono channel
                '-ar', '44100',          # 44.1 kHz sample rate
                '-y',                    # Overwrite output file
                wav_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Successfully converted to {os.path.basename(wav_file)}")
                # Remove the original MP3 file
                os.remove(mp3_file)
                print(f"  Removed original MP3 file")
            else:
                print(f"✗ Error converting {os.path.basename(mp3_file)}:")
                print(f"  {result.stderr}")
                
        except Exception as e:
            print(f"✗ Exception while converting {os.path.basename(mp3_file)}: {e}")
    
    print(f"\nConversion complete!")

def verify_wav_files(input_folder):
    """Verify all WAV files are in the correct format"""
    
    wav_files = glob.glob(os.path.join(input_folder, "*.wav"))
    
    if not wav_files:
        print("No WAV files found.")
        return
    
    print(f"\nVerifying {len(wav_files)} WAV files:")
    
    for wav_file in wav_files:
        try:
            # Use ffprobe to get file information
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                wav_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                if 'streams' in info and len(info['streams']) > 0:
                    stream = info['streams'][0]
                    
                    sample_rate = int(stream.get('sample_rate', 0))
                    channels = int(stream.get('channels', 0))
                    codec_name = stream.get('codec_name', '')
                    
                    print(f"  {os.path.basename(wav_file)}:")
                    print(f"    - Sample Rate: {sample_rate} Hz")
                    print(f"    - Channels: {channels}")
                    print(f"    - Codec: {codec_name}")
                    
                    if sample_rate == 44100 and channels == 1 and codec_name == 'pcm_s16le':
                        print(f"    ✓ Format is correct")
                    else:
                        print(f"    ⚠ Format may need adjustment")
                else:
                    print(f"  {os.path.basename(wav_file)}: Could not read stream info")
            else:
                print(f"  {os.path.basename(wav_file)}: Error reading file info")
                
        except Exception as e:
            print(f"  {os.path.basename(wav_file)}: Exception - {e}")

if __name__ == "__main__":
    input_folder = "wav_audio_correct"
    
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        exit(1)
    
    print("Converting MP3 files to WAV format...")
    convert_mp3_to_wav(input_folder)
    
    print("\nVerifying WAV file formats...")
    verify_wav_files(input_folder)
    
    print("\nAll files in wav_audio_correct are now ready for testing!") 