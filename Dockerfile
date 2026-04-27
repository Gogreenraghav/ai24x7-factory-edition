# AI24x7 Factory Edition — Docker Image
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3-pip python3.10-venv \
    ffmpeg libsm6 libxext6 libgl1-mesa-glx libglib2.0-0 \
    curl wget git htop vim net-tools ca-certificates \
    libcairo2 libpango-1.0-0 libgirepository1.0-dev libffi-dev pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /opt/ai24x7-factory
COPY factory/ /opt/ai24x7-factory/factory/

RUN pip install --no-cache-dir --upgrade pip \
    streamlit pandas pillow numpy psutil schedule requests \
    python-dotenv httpx aiohttp fastapi uvicorn pydantic pydantic-settings \
    sqlalchemy python-multipart stripe gtts edge-tts opencv-python \
    python-telegram-bot

RUN mkdir -p /data/models /data/db /data/logs /data/config /data/captures /opt/llama-server

COPY .env /opt/ai24x7-factory/.env
COPY start.sh /opt/ai24x7-factory/start.sh
COPY healthcheck.py /opt/ai24x7-factory/healthcheck.py
RUN chmod +x /opt/ai24x7-factory/start.sh /opt/ai24x7-factory/healthcheck.py

EXPOSE 5050 5051 5052 5053 5054 5055 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 /opt/ai24x7-factory/healthcheck.py || exit 1
CMD ["/opt/ai24x7-factory/start.sh"]
