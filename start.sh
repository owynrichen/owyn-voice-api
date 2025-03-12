#! /bin/bash
if [ ! -e "/asset-vol/prompts/owyntest2.npz" ]; then
    cp -R /app/owyn-voice-api/assets-backup/* /asset-vol
fi

if [ ! -e "/asset-vol/output" ]; then
    mkdir /asset-vol/output
fi

/root/.local/bin/poetry run fastapi run owyn-voice-api --port 8675