import os

from .voice_model import VoiceModel
from bark.api import generate_audio
from bark.generation import SAMPLE_RATE, codec_decode, preload_models, generate_coarse, generate_fine, generate_text_semantic
from scipy.io.wavfile import write as write_wav

class BarkModel(VoiceModel):
    def __init__(self):
        super().__init__("bark")

        # preload bark models
        print("Preloading Bark models...")
        preload_models(
            text_use_gpu=True,
            text_use_small=True,
            coarse_use_gpu=True,
            coarse_use_small=True,
            fine_use_gpu=True,
            fine_use_small=True,
            codec_use_gpu=True,
            force_reload=False
        )
    
    def support_voice_name(self, voice_name: str) -> bool:
        return os.path.exists(f"{self.base_service_path}/assets/prompts/{voice_name}.npz")
    
    def write_audio(self, voice_name: str, prompt: str, text_temp=0.7, waveform_temp=0.7) -> str:
        audio_path = self.build_audio_path(prompt, voice_name, text_temp=text_temp, waveform_temp=waveform_temp)
        
        full_voice_path = f"{self.base_service_path}/assets/prompts/{voice_name}.npz"
        audio_array = generate_audio(prompt, history_prompt=full_voice_path, text_temp=text_temp, waveform_temp=waveform_temp)
        write_wav(audio_path, SAMPLE_RATE, audio_array)
        
        return audio_path