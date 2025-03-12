FROM python:3.12-slim AS owyn-voice-api-build

RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    git \
    git-lfs \
    mecab \
    libmecab-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
RUN mkdir /asset-vol
VOLUME /asset-vol

COPY pyproject.toml /app/pyproject.toml
RUN /root/.local/bin/poetry install -E cpu -v --no-cache --compile && \
/root/.local/bin/poetry cache list | awk '{print "/root/.local/bin/poetry cache clear --all -n " $1}' | sh
RUN /root/.local/bin/poetry run python -m unidic download

# checkout the openvoice checkpoint - find a way to combine these to
# avoid saving the .git directory, OR, expect it to be available and
# copy directly
# COPY .gitattributes .git /app/
# RUN git lfs fetch && git lfs checkout; \
#     rm -rf /app/.git
COPY ./owyn-voice-api /app/owyn-voice-api

# the copy of asset-backup happens in start.sh at runtime

RUN mv /app/owyn-voice-api/assets /app/owyn-voice-api/assets-backup && \
    ln -s /asset-vol /app/owyn-voice-api/assets

RUN ln -s /asset-vol/output /app/output
COPY .env /app/.env
COPY ./start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["./start.sh"]