from .voice_model import VoiceModel
from melo.api import TTS
import torch, torchaudio
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
import os


class OpenVoiceModel(VoiceModel):
    def __init__(self):
        super().__init__("openvoice")

        # preload openvoice and set it up
        print("Preloading OpenVoice models...")
        language = "EN"
        device = "cuda"

        ckpt_converter = f'{self.base_service_path}/assets/openvoice/converter'
        self.tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
        self.tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

        self.model = TTS(language=language, device=device)

        speaker_ids = self.model.hps.data.spk2id
        self.speaker_id = speaker_ids["EN-US"]
        speaker_key = "en-us"
        self.source_se = torch.load(f'{self.base_service_path}/assets/openvoice/checkpointsV2/ses/{speaker_key}.pth', map_location=device)

    
    def support_voice_name(self, voice_name: str) -> bool:
        return os.path.exists(f"{self.base_service_path}/assets/openvoice/{voice_name}.mp3")
    
    def _write_audio(self, voice_name: str, prompt: str, audio_path: str, audio_filename: str, mimetype:str, speed=1.0, **kwargs) -> str:
        reference_speaker = f"{self.base_service_path}/assets/openvoice/{voice_name}.mp3"
        target_se, audio_name = se_extractor.get_se(reference_speaker, self.tone_color_converter, vad=False)
        
        src_path = f"{audio_path}.tmp.{self.get_filetype()[1]}"
        self.model.tts_to_file(prompt, self.speaker_id, src_path, speed=speed)

        # Run the tone color converter
        encode_message = "@MyShell"
        self.tone_color_converter.convert(
            audio_src_path=src_path, 
            src_se=self.source_se, 
            tgt_se=target_se, 
            output_path=audio_path,
            message=encode_message)
        
        return audio_path