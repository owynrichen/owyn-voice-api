from typing import Union

import asyncio

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from bark.api import generate_audio
from bark.generation import SAMPLE_RATE, codec_decode, preload_models, generate_coarse, generate_fine, generate_text_semantic
import hashlib
import os

from melo.api import TTS
import torch, torchaudio
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

from scipy.io.wavfile import write as write_wav


# TODO: clean this up so it's not inlined in main
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


# preload openvoice and set it up
print("Preloading OpenVoice models...")
language = "EN"
device = "cuda"

CUR_PATH = os.path.dirname(os.path.realpath(__file__))

ckpt_converter = f'{CUR_PATH}/assets/openvoice/converter'
tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

model = TTS(language=language, device=device)

speaker_ids = model.hps.data.spk2id
speaker_id = speaker_ids["EN-US"]
speaker_key = "en-us"
source_se = torch.load(f'{CUR_PATH}/assets/openvoice/checkpointsV2/ses/{speaker_key}.pth', map_location=device)

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

openvoice_names = {
    'owyn-reference3': 'owyn-reference3'
}

def build_audio_path(prompt, voice_name, text_temp, waveform_temp):
    audio_key = f"{voice_name}|{prompt}|{text_temp}|{waveform_temp}"
    m = hashlib.md5()
    m.update(audio_key.encode('utf-8'))
    audio_hash = m.hexdigest()
    audio_path = f"./output/{voice_name}-{audio_hash}.wav"
    return audio_path

def write_bark_audio(audio_path, prompt, voice_name, text_temp, waveform_temp):
    full_voice_path = f"{CUR_PATH}/assets/prompts/{voice_name}.npz"
    audio_array = generate_audio(prompt, history_prompt=full_voice_path, text_temp=text_temp, waveform_temp=waveform_temp)
    write_wav(audio_path, SAMPLE_RATE, audio_array)
    return audio_array

def write_openvoice_audio(audio_path, prompt, voice_name, speed=1.0):
    reference_speaker = f"{CUR_PATH}/assets/openvoice/{voice_name}.mp3"
    target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)
    src_path = f"{audio_path}.tmp.wav"
    model.tts_to_file(prompt, speaker_id, src_path, speed=speed)

    # Run the tone color converter
    encode_message = "@MyShell"
    tone_color_converter.convert(
        audio_src_path=src_path, 
        src_se=source_se, 
        tgt_se=target_se, 
        output_path=audio_path,
        message=encode_message)

@app.get("/speak_as/{voice_name}")
async def speak_as(prompt:str, voice_name: str = "owyn-reference3", text_temp=0.7, waveform_temp=0.7, speed=1.0, bypass_cache=False):
    assert(prompt != None)
    assert(voice_name != None)
    assert(text_temp != None)
    assert(waveform_temp != None)

    audio_path = build_audio_path(prompt, voice_name, text_temp, waveform_temp)

    if bypass_cache or not os.path.exists(audio_path):
        if voice_name in openvoice_names.keys():
            write_openvoice_audio(audio_path, prompt, voice_name, speed=speed)
        else:
            write_bark_audio(audio_path, prompt, voice_name, text_temp, waveform_temp)
    
    return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")
