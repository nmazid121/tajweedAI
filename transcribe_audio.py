# Import the model from huggingface
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(model_name="nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0")



# Transcribe's Ayah 1 from Surah Falaq - Mishary Rashid Al Afasy
output = asr_model.transcribe(['all_audio_data/wav_audio_correct/nabhan_incorrect_qalqalah.wav'])
print(output[0].text)