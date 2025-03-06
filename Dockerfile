FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    python3-pip \
    git \
    git-lfs \
    mecab \
    libmecab-dev \
    ffmpeg

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . /app

# checkout the openvoice checkpoint

# RUN git lfs install
RUN git lfs fetch
RUN git lfs checkout

RUN export PATH="/root/.local/bin:$PATH"
RUN /root/.local/bin/poetry install -E cpu -v
RUN /root/.local/bin/poetry run python -m unidic download

CMD ["/root/.local/bin/poetry", "run", "fastapi", "run", "owyn-voice-api", "--port", "8675"]