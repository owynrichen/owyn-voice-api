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

    def get_filetype(self) -> str:
        return "audio/wav", "wav"

    def build_audio_path(self, prompt: str, voice_name: str, **kwargs) -> str:
        audio_key = f"{voice_name}|{prompt}|{kwargs}"
        m = hashlib.md5()
        m.update(audio_key.encode('utf-8'))
        audio_hash = m.hexdigest()
        mime_type, filetype = self.get_filetype()
        audio_filename = f"{voice_name}-{audio_hash}.{filetype}"
        audio_path = f"{self.base_audio_path}{audio_filename}"

        return audio_path, audio_filename, mime_type

    def write_audio(self, voice_name: str, prompt: str, **kwargs) -> str:
        audio_path, audio_filename, mimetype = self.build_audio_path(prompt, voice_name, **kwargs)

        bypass_cache = kwargs.get("bypass_cache", False)

        if bypass_cache or not os.path.exists(audio_path):
            print(f"Generating audio for {voice_name} with prompt: {prompt}")
            audio_path = self._write_audio(voice_name, prompt, audio_path, audio_filename, mimetype, **kwargs)
        else:
            print(f"Audio already exists for {voice_name} with prompt: {prompt}, returning cached value")

        return audio_path, audio_filename, mimetype

    def _write_audio(self, voice_name: str, prompt: str, audio_path: str, audio_filename: str, mimetype:str, **kwargs) -> str:
        raise NotImplementedError("This method should be overridden in subclasses.")