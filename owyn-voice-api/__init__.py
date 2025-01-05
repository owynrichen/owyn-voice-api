from typing import Union

import asyncio

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from bark.api import generate_audio
from bark.generation import SAMPLE_RATE, codec_decode, preload_models, generate_coarse, generate_fine, generate_text_semantic
import hashlib
import os

from scipy.io.wavfile import write as write_wav

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

CUR_PATH = os.path.dirname(os.path.realpath(__file__))

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/speak_as/{voice_name}")
async def speak_as(prompt:str, voice_name: str = "owyntest2", text_temp=0.7, waveform_temp=0.7, bypass_cache=False):
    assert(prompt != None)
    assert(voice_name != None)
    assert(text_temp != None)
    assert(waveform_temp != None)

    audio_key = f"{voice_name}|{prompt}|{text_temp}|{waveform_temp}"
    m = hashlib.md5()
    m.update(audio_key.encode('utf-8'))
    audio_hash = m.hexdigest()
    audio_path = f"./output/{audio_hash}.wav"

    if bypass_cache or not os.path.exists(audio_path):
        full_voice_path = f"{CUR_PATH}/assets/prompts/{voice_name}.npz"
        audio_array = generate_audio(prompt, history_prompt=full_voice_path, text_temp=0.7, waveform_temp=0.7)
        write_wav(audio_path, SAMPLE_RATE, audio_array)
    
    return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")