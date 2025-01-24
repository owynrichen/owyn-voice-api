import hashlib, os

class VoiceModel:
    def __init__(self, model_id: str, base_service_path=os.path.dirname(os.path.realpath(__file__)), base_audio_path="./output/"):
        self.model_id = model_id
        self.base_audio_path = base_audio_path
        self.base_service_path = base_service_path

    def __repr__(self) -> str:
        return f"VoiceModel(model_id={self.model_id})"
    
    def __str__(self) -> str:
        return self.model_id

    def support_voice_name(self, voice_name: str) -> bool:
        return False
    
    def build_audio_path(self, prompt: str, voice_name: str, **kwargs) -> str:
        audio_key = f"{voice_name}|{prompt}|{kwargs}"
        m = hashlib.md5()
        m.update(audio_key.encode('utf-8'))
        audio_hash = m.hexdigest()
        audio_path = f"{self.base_audio_path}{voice_name}-{audio_hash}.wav"

        return audio_path
    
    def write_audio(self, voice_name: str, prompt: str, **kwargs) -> str:
        raise NotImplementedError("This method should be overridden in subclasses.")