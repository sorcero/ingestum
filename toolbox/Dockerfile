FROM registry.fedoraproject.org/f32/fedora-toolbox

RUN dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-32.noarch.rpm && \
    dnf -y install \
    git gcc \
    pip python-devel python3-virtualenv \
    libSM libXrender libXext \
    poppler-utils sox attr ffmpeg \
    ghostscript tesseract \
    libXScrnSaver gtk3 && \
    dnf clean all

ADD https://download.documentfoundation.org/libreoffice/stable/7.1.1/rpm/x86_64/LibreOffice_7.1.1_Linux_x86-64_rpm.tar.gz \
    /tmp/libreoffice.tar.gz
RUN (tar -xvf /tmp/libreoffice.tar.gz -C /tmp/ && \
    cd /tmp/LibreOffice_7.1.1.2_Linux_x86-64_rpm/RPMS/ && \
    dnf -y install libobasis7.1-writer-7.1.1.2-2.x86_64.rpm libobasis7.1-calc-7.1.1.2-2.x86_64.rpm libobasis7.1-en-US-7.1.1.2-2.x86_64.rpm libobasis7.1-ooofonts-7.1.1.2-2.x86_64.rpm libobasis7.1-core-7.1.1.2-2.x86_64.rpm libobasis7.1-images-7.1.1.2-2.x86_64.rpm libobasis7.1-graphicfilter-7.1.1.2-2.x86_64.rpm libreoffice7.1-7.1.1.2-2.x86_64.rpm libreoffice7.1-ure-7.1.1.2-2.x86_64.rpm libreoffice7.1-freedesktop-menus-7.1.1-2.noarch.rpm && \
    dnf clean all && \
    rm -rf /tmp/libre* /tmp/Libre*)

ENV INGESTUM_DEEPSPEECH_DIR=/opt/sorcero/deepspeech
ADD https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm \
    /opt/sorcero/deepspeech/models.pbmm
ADD https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer \
    /opt/sorcero/deepspeech/models.scorer
RUN chmod 644 /opt/sorcero/deepspeech/models.*

RUN git clone https://gitlab.com/sorcero/community/ingestum /opt/sorcero/ingestum && \
    pip install /opt/sorcero/ingestum && \
    rm -rf /opt/sorcero/ingestum
