# import the model from huggingface
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(model_name="nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0")

# transcribe's Ayah 1 from Surah Falaq - Mishary Rashid Al Afasy
output = asr_model.transcribe(['surah_falaq_ayah_1_nabhan.wav'])
print(output[0].text)