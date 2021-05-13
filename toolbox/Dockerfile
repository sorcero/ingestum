FROM registry.fedoraproject.org/f32/fedora-toolbox

RUN dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-32.noarch.rpm && \
    dnf -y install \
    git gcc \
    pip python-devel python3-virtualenv \
    libSM libXrender libXext \
    poppler-utils sox attr ffmpeg \
    ghostscript tesseract \
    libXScrnSaver gtk3 \
    libreoffice-writer libreoffice-calc libreoffice-graphicfilter && \
    dnf clean all

ENV INGESTUM_DEEPSPEECH_DIR=/opt/sorcero/deepspeech
ADD https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm \
    /opt/sorcero/deepspeech/models.pbmm
ADD https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer \
    /opt/sorcero/deepspeech/models.scorer
RUN chmod 644 /opt/sorcero/deepspeech/models.*

RUN git clone https://gitlab.com/sorcero/community/ingestum /opt/sorcero/ingestum && \
    pip install /opt/sorcero/ingestum && \
    rm -rf /opt/sorcero/ingestum
