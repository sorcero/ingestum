# Use official Ubuntu 20.04 LTS image as base
FROM ubuntu:20.04

# Set an environment variable to point to the location where DeepSpeech models are stored
ENV INGESTUM_DEEPSPEECH_DIR=/opt/sorcero/deepspeech
# Download DeepSpeech models to /opt/sorcero/deepspeech/
ADD https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm \
    /opt/sorcero/deepspeech/models.pbmm
ADD https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer \
    /opt/sorcero/deepspeech/models.scorer
# Set models permissions: user (read/write), group and others (read)
RUN chmod 644 /opt/sorcero/deepspeech/models.*

# Run dpkg (behind apt) without interactive dialogue
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies and clear apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential git \
    python3-pip python3-dev python3-virtualenv \
    poppler-utils sox attr ffmpeg \
    libsm-dev libxrender-dev libxext-dev libxss-dev libgtk-3-dev \
    ghostscript tesseract-ocr sudo openssh-client && \
    apt-get install -y libreoffice && \
    apt-get clean

# Clone ingestum repository, install package (including dependencies), and remove source code
RUN git clone https://gitlab.com/sorcero/community/ingestum /opt/sorcero/ingestum && \
    pip install /opt/sorcero/ingestum && \
    rm -rf /opt/sorcero/ingestum

# Set working directory as '/ingestum' (can bind mount this directory with a host directory)
WORKDIR /ingestum
