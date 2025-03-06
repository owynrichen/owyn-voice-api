# owyn-voice-api

https://github.com/serp-ai/bark-with-voice-clone/
https://github.com/suno-ai/bark
https://github.com/lucaspar/poetry-torch

https://github.com/Zyphra/Zonos?tab=readme-ov-file

```bash
git lfs checkout # for the openvoice checkpoint
git lfs fetch
poetry install --sync -E cuda --with cuda
poetry run python -m unidic download # for MeloTTS/OpenVoice
```

```bash
cp .env.example .env
vim .env
# fill in the proper variable in the .env
poetry run fastapi run owyn-voice-api --port 8675
```

# Docker/Podman

To run this in a container, you can (using [podman](https://podman.io/)) run the following:

```bash
podman build .
```