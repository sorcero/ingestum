Installation Guide
==================

This guide will take you through the process of installing the Sorcero
Ingestion library on your machine.

1. Simplified installation
--------------------------

The simplest way of getting Ingestum running is to build and use a
toolbox container. Toolbox makes it easy to use a containerized
environment for everyday software development. Therefore, we provide
a Dockerfile to get started in no time::

    $ sudo dnf -y install git toolbox
    $ git clone https://gitlab.com/sorcero/community/ingestum
    $ cd ingestum/toolbox
    $ podman build . -t ingestum-toolbox:latest
    $ toolbox create -c ingestum-toolbox -i ingestum-toolbox
    $ toolbox enter ingestum-toolbox

2. Manual installation
----------------------

.. warning::

    Ingestum was developed for Fedora 32 (Linux). It may still work
    on other operating systems (especially ones that are unix-based) but be
    aware that some or most features may not work. If you don't have a
    computer that runs Fedora, consider using a `VirtualBox
    <https://www.virtualbox.org/>`_ VM.

.. |br| raw:: html

    <br>

3. Download the system dependencies
-----------------------------------

The following dependencies are used for audio ingestion::

    $ sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
    $ sudo dnf install pip gcc python-devel python3-virtualenv libSM libXrender libXext poppler-utils sox attr ffmpeg ghostscript tesseract libXScrnSaver gtk3 libreoffice-writer libreoffice-calc libreoffice-graphicfilter
    $ mkdir ~/.deepspeech
    $ wget -O ~/.deepspeech/models.pbmm https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm
    $ wget -O ~/.deepspeech/models.scorer https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer

4. Download the library
-----------------------

Use ``git clone`` or some other method to download the ``ingestum``
library. You'll need a personal access token to use HTTPS if you don't already
have one (User Settings > Access Tokens). The last command is optional but will
be useful as it saves your authentication information::

    $ git clone https://gitlab.com/sorcero/community/ingestum.git

5. Install the library
----------------------

You'll also need to download ``virtualenv`` if you don't already have it::

    $ pip install virtualenv
    $ virtualenv env
    $ source ./env/bin/activate
    $ pip install .

6. Set the plugins directory
----------------------------

The default location of the plugins directory is::

    $HOME/.ingestum/plugins

(Optional) This environment variable is used for specifying the
location of the plugins directory::

    export INGESTUM_PLUGINS_DIR=""


7. Set your authentication credentials
--------------------------------------

(Optional) These environment variables are used for Twitter feed
ingestion::

    export INGESTUM_TWITTER_CONSUMER_KEY=""
    export INGESTUM_TWITTER_CONSUMER_SECRET=""
    export INGESTUM_TWITTER_ACCESS_TOKEN=""
    export INGESTUM_TWITTER_ACCESS_SECRET=""

(Optional) These environment variables are used for Email ingestion::

    export INGESTUM_EMAIL_HOST=""
    export INGESTUM_EMAIL_PORT=""
    export INGESTUM_EMAIL_USER=""
    export INGESTUM_EMAIL_PASSWORD=""

(Optional) These environment variables are used for ProQuest
ingestion::

    export INGESTUM_PROQUEST_ENDPOINT=""
    export INGESTUM_PROQUEST_TOKEN=""

(Optional) These environment variables are used for PubMed
ingestion::

    export INGESTUM_PUBMED_TOOL=""
    export INGESTUM_PUBMED_EMAIL=""
