from pydub import AudioSegment
import os

src_folder = "3_falaq_word_approach/final_neg_samples_mp3"
for fname in os.listdir(src_folder):
    if fname.lower().endswith('.mp3'):
        mp3_path = os.path.join(src_folder, fname)
        wav_path = os.path.join(src_folder, os.path.splitext(fname)[0] + ".wav")
        audio = AudioSegment.from_mp3(mp3_path)
        audio = audio.set_channels(1)
        audio.export(wav_path, format="wav")
        print(f"Converted {fname} -> {os.path.basename(wav_path)}")