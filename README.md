# owyn-voice-api

https://github.com/serp-ai/bark-with-voice-clone/
https://github.com/suno-ai/bark
https://github.com/lucaspar/poetry-torch

```bash
git lfs checkout # for the openvoice checkpoint
poetry install --sync -E cuda --with cuda
poetry run python -m unidic download # for MeloTTS/OpenVoice
```

```bash
export CLOUDFLARE_API_TOKEN="your cloudflare API key"
export CLOUDFLARE_ACCOUNT_ID="your cloudflare account id"
export CLOUDFLARE_KV_ID="your cloudflare KV id"
poetry run fastapi run owyn-voice-api --port 8675
```