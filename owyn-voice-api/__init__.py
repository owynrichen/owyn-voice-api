import asyncio, os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .bark_voice_model import BarkModel
from .elevenlabs_voice_model import ElevenLabsModel
from .openvoice_voice_model import OpenVoiceModel

# initialize the models
print("Initializing models...")
models = {
        "bark": BarkModel(),
        "openvoice": OpenVoiceModel(),
        "elevenlabs": ElevenLabsModel()
}

print("Models initialized.")
print("Starting server...")

app = FastAPI()

origins = [
    "https://owynrichen.com",
    "https://*.owynrichen.com",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/speak_as/{voice_name}")
async def speak_as(prompt:str, voice_name: str = "owyn-reference3", text_temp=0.7, waveform_temp=0.7, speed=1.0, bypass_cache=False):
    assert(prompt != None)
    assert(voice_name != None)
    assert(text_temp != None)
    assert(waveform_temp != None)

    for model in models.values():
        if model.support_voice_name(voice_name):
            print (f"Using model: {model.model_id} for voice: {voice_name}")
            audio_path, audio_filename, mimetype = model.write_audio(voice_name, prompt, text_temp=text_temp, waveform_temp=waveform_temp, speed=speed)
            return FileResponse(audio_path, media_type=mimetype, filename=audio_filename)
    
    raise ValueError(f"Voice {voice_name} is not supported by any model.")
