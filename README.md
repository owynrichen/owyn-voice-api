# owyn-voice-api

https://github.com/serp-ai/bark-with-voice-clone/
https://github.com/suno-ai/bark
https://github.com/lucaspar/poetry-torch

```bash
poetry install --sync -E cuda --with cuda
poetry run python -m unidic download # for MeloTTS/OpenVoice
```

```bash
export CLOUDFLARE_EMAIL="your cloudflare email address"
export CLOUDFLARE_API_KEY="your cloudflare API key"
poetry run fastapi run owyn-voice-api --port 8675
```