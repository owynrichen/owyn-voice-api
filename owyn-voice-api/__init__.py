import asyncio, os

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import torch

from .bark_voice_model import BarkModel
from .elevenlabs_voice_model import ElevenLabsModel
from .openvoice_voice_model import OpenVoiceModel

load_dotenv()

class Models:
    def __init__(self):
        self.models = None

    def values(self) -> list:
        # lazy-initialize the models
        if self.models is None:
        # initialize the models
            print("Initializing models...")
            self.models = {
                    "elevenlabs": ElevenLabsModel()
            }

            if torch.cuda.is_available():
                print("CUDA available, initializing CUDA models...")
                self.models["bark"] = BarkModel()
                self.models["openvoice"] = OpenVoiceModel()

            print(f"Models initialized. {self.models.keys()}")

        return self.models.values()

models = Models()
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
