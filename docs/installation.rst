Installation Guide
==================

This guide will take you through the process of installing the Sorcero
Ingestion library on your machine.

Simplified installation
-----------------------

The simplest way of getting Ingestum running is to use a Docker container
bind-mounted with a folder on your host system. In this way, you can use the
Docker container as an execution sandbox while using the files and apps
(code editors, PDF viewers, etc.) on your host system.

To install Docker, visit `Get Docker
<https://docs.docker.com/get-docker/>`_.

.. code-block:: bash

    $ git clone https://gitlab.com/sorcero/community/ingestum
    $ cd ingestum/docker
    $ docker build -t ingestum:latest .
    $ docker run -it --rm --name ingestum --mount type=bind src=/absolute/path/on/host dst=/app ingestum:latest

If you running Fedora, you can also use a toolbox container. Toolbox makes it easy
to use a containerized environment for everyday software development. Therefore,
we provide a `Dockerfile` to get started in no time:

.. code-block:: bash

    $ sudo dnf -y install git toolbox
    $ git clone https://gitlab.com/sorcero/community/ingestum
    $ cd ingestum/toolbox
    $ podman build . -t ingestum-toolbox:latest
    $ toolbox create -c ingestum-toolbox -i ingestum-toolbox
    $ toolbox enter ingestum-toolbox

.. warning::

    Ingestum won't fully work on `AARCH64`/`ARM64` systems as two Python modules
    (``opencv-python`` and ``deepspeech``) won't install. See
    :ref:`manual installation steps<manual-installation>` for workaround.

.. _manual-installation:

Manual installation
-------------------

.. warning::

    Ingestum was developed for `Ubuntu 20.04` (`Linux`). It may still work
    on other operating systems (especially ones that are `unix-based`) but be
    aware that some or most features may not work. If you don't have a
    computer that runs `Ubuntu`, consider using a `VirtualBox
    <https://www.virtualbox.org/>`_ VM or a `Docker
    <https://docs.docker.com/get-docker/>`_ container from a `Ubuntu 20.04` image.

.. |br| raw:: html

    <br>

1. Download the system dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the following system dependencies:

.. code-block:: bash

    $ sudo apt -y install python3-pip python3-dev python3-virtualenv libsm-dev libxrender-dev libxext-dev libxss-dev libgtk-3-dev poppler-utils sox attr ffmpeg ghostscript tesseract-ocr
    $ sudo apt-get -y install libreoffice

For `AARCH64`/`ARM64`, you need one more dependency (``libxslt-dev``):

.. code-block:: bash

    $ sudo apt -y install libxslt-dev

The following dependencies are used for audio ingestion:

.. code-block:: bash

    $ mkdir ~/.deepspeech
    $ wget -O ~/.deepspeech/models.pbmm https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.pbmm
    $ wget -O ~/.deepspeech/models.scorer https://github.com/mozilla/DeepSpeech/releases/download/v0.7.3/deepspeech-0.7.3-models.scorer

For `AARCH64`/`ARM64`, you need ``deepspeech 0.9.3`` instead:

.. code-block:: bash

    $ mkdir ~/.deepspeech
    $ wget -O ~/.deepspeech/models.pbmm https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm
    $ wget -O ~/.deepspeech/models.scorer https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer

2. Download the library
~~~~~~~~~~~~~~~~~~~~~~~

Use ``git clone`` or some other method to download the ``ingestum``
library.

.. code-block:: bash

    $ git clone https://gitlab.com/sorcero/community/ingestum.git

3. Install the library
~~~~~~~~~~~~~~~~~~~~~~

You'll need to download ``virtualenv`` if you don't already have it:

.. code-block:: bash

    $ sudo apt install python3-venv
    $ virtualenv env

or simply:

.. code-block:: bash

    $ python3 -m venv env

Install the dependencies:

.. code-block:: bash

    $ source ./env/bin/activate
    $ pip install .

.. warning::

    On `AARCH64`/`ARM64`, ``pip install .`` will fail because `pip` won't be able to
    install ``deepspeech 0.7.3`` and ``opencv-python 4.2.0.34``. There's no way to
    install ``opencv-python`` for the time being, but ``deepspeech 0.9.3`` can be
    installed. In the ``requirements.txt`` file, replace ``deepspeech==0.7.3`` with
    ``deepspeech==0.9.3``, and remove ``opencv-python==4.2.0.34``. You can then go
    ahead with ``pip install .``.

    Since `OpenCV` will not be installed, any transformer (e.g.
    ``image_source_create_tabular_document``) that requires it (``cv2``), will
    crash. The rest should work fine.

4. Set the plugins directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default location of the plugins directory is:

.. code-block:: bash

    $HOME/.ingestum/plugins

(`optional`) This environment variable is used for specifying the
location of the plugins directory:

.. code-block:: bash

    export INGESTUM_PLUGINS_DIR=""


5. Set your authentication credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(`optional`) These environment variables are used for Twitter feed
ingestion:

.. code-block:: bash

    export INGESTUM_TWITTER_CONSUMER_KEY=""
    export INGESTUM_TWITTER_CONSUMER_SECRET=""
    export INGESTUM_TWITTER_ACCESS_TOKEN=""
    export INGESTUM_TWITTER_ACCESS_SECRET=""

(`optional`) These environment variables are used for Email ingestion:

.. code-block:: bash

    export INGESTUM_EMAIL_HOST=""
    export INGESTUM_EMAIL_PORT=""
    export INGESTUM_EMAIL_USER=""
    export INGESTUM_EMAIL_PASSWORD=""

(`optional`) These environment variables are used for ProQuest ingestion:

.. code-block:: bash

    export INGESTUM_PROQUEST_ENDPOINT=""
    export INGESTUM_PROQUEST_TOKEN=""

(`optional`) These environment variables are used for PubMed ingestion:

.. code-block:: bash

    export INGESTUM_PUBMED_TOOL=""
    export INGESTUM_PUBMED_EMAIL=""

(`optional`) These environment variables are used for Reddit ingestion
(from https://www.reddit.com/prefs/apps):

.. code-block:: bash

    export INGESTUM_REDDIT_CLIENT_ID=""
    export INGESTUM_REDDIT_CLIENT_SECRET=""


6. Set active worker
~~~~~~~~~~~~~~~~~~~~

Ingestum can work in single-processed or multi-processed mode. A construct —
`workers` is used to control the mode. The default worker is ``legacy`` which is
single-processed. To use multiprocessing, set the ``INGESTUM_WORKER`` variable
to ``multiprocessed``, and ``INGESTUM_MULTIPROCESSING_DEGREE`` to the number of
CPU cores you want. The degree of multiprocessing, if not provided defaults to
the number of available CPU cores.

(`optional`) These environment variables are used to control multiprocessing:

.. code-block:: bash

    export INGESTUM_WORKER=""
    export INGESTUM_MULTIPROCESSING_DEGREE=""

(`optional`) To log the run-time of parallel workers:

.. code-block:: bash

    export INGESTUM_WORKER_LOG_TIME=1
