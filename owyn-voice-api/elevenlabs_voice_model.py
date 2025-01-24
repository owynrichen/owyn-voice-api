from .voice_model import VoiceModel

from cloudflare import Cloudflare
from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
import os

class ElevenLabsModel(VoiceModel):
    def __init__(self):
        super().__init__("elevenlabs")
        
        print("Configuring ElevenLabs models...")

        self.cf_client = Cloudflare(
            api_email=os.environ.get("CLOUDFLARE_EMAIL"),  # This is the default and can be omitted
            api_key=os.environ.get("CLOUDFLARE_API_KEY"),  # This is the default and can be omitted
        )
        api_kv = self.cf_client.kv.namespaces.values.get(
            key_name="elevenlabs-api-key",
            account_id=os.environ.get("CLOUDFLARE_ACCOUNT_ID"),
            namespace_id=os.environ.get("CLOUDFLARE_KV_ID"), # voice-clone-kv
        )
        print(api_kv)
        api_key = api_kv.read()
        print(f"ElevenLabs key: {api_key}")

        self.client = ElevenLabs(api_key=api_key)
        self.setup_voices()
        

    def setup_voices(self) -> None:
        self.voices = {}

        el_voices = self.client.voices.get_all().voices
        print(el_voices)
        for voice in el_voices:
            self.voices[voice.name] = voice.id
    
    def get_voice_name(self, voice_name: str) -> str:
        return voice_name.replace("el:", "")

    def support_voice_name(self, voice_name: str) -> bool:
        el_voicename = self.get_voice_name(voice_name)
        return el_voicename in self.voices.keys()
    
    def get_voice_settings(self, voice_name: str, **kwargs) -> VoiceSettings:
        return VoiceSettings(
            stability=kwargs.get("stability", 0.75),
            similarity_boost=kwargs.get("similarity_boost", 0.75),
            use_speaker_boost=kwargs.get("use_speaker_boost", True)
        )
    
    def get_voice(self, voice_name: str, **kwargs) -> str:
        return Voice(
            voice_id=self.voices[self.get_voice_name(voice_name)],
            settings=self.get_voice_settings(voice_name, **kwargs)
        )
    
    def write_audio(self, voice_name: str, prompt: str, **kwargs) -> str:
        audio_path = self.build_audio_path(prompt, voice_name, **kwargs)

        audio = self.client.generate(
            text=prompt,
            voice=self.get_voice(voice_name, **kwargs),
            model="eleven_multilingual_v2",
            stream=False,
            output_format="pcm_24000"
        )

        save(audio, audio_path)

        return audio_path

