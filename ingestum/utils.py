# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Sorcero, Inc.
#
# This file is part of Sorcero's Language Intelligence platform
# (see https://www.sorcero.com).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import os
import re
import json
import requests
import youtube_dl
import sox
import ffmpeg
import tempfile
import mimetypes
import logging

from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from json.decoder import JSONDecodeError
from nltk.tokenize import RegexpTokenizer

from requests_cache import CachedSession

PATTERN = r"""(?x)
      (?:[A-Z]\.)+
      | \w+(?:-\w+)*
     """

__logger__ = logging.getLogger("ingestum")


# XXX fixes missing mimetype
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xlsx",
)


def find_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in find_subclasses(c)]
    )


def safe_json_load(string):
    try:
        return json.loads(string)
    except (TypeError, JSONDecodeError) as e:
        __logger__.error(f"{__name__} %s", e)
        return None


def get_transformer_by_name(name):
    module = __import__("ingestum.transformers.%s" % name)
    submodule = getattr(module, "transformers")
    submodule = getattr(submodule, name)
    return submodule.Transformer


def get_conditional_by_name(name):
    module = __import__("ingestum.conditionals.%s" % name)
    submodule = getattr(module, "conditionals")
    submodule = getattr(submodule, name)
    return submodule.Conditional


def get_source_by_name(name):
    module = __import__("ingestum.sources.%s" % name)
    submodule = getattr(module, "sources")
    submodule = getattr(submodule, name)
    return submodule.Source


def get_document_class_by_type(name):
    module = __import__("ingestum.documents.%s" % name)
    submodule = getattr(module, "documents")
    submodule = getattr(submodule, name)
    return submodule.Document


def get_document_from_path(path):
    from pydantic import BaseModel
    from typing import Union
    from . import documents

    class Parser(BaseModel):
        document: Union[tuple(find_subclasses(documents.base.BaseDocument))]

    with open(path) as json_file:
        document = json.loads(json_file.read())

    parsed = Parser(document=document)

    return parsed.document


def tokenize(words):
    """
    Parameters
    ----------
    words : str
        A single string

    Returns
    -------
    tokenizer : object
        Containing tokens extracted from words
    """
    tokenizer = RegexpTokenizer(PATTERN)
    return tokenizer.tokenize(words)


def preprocess_video(name, content):
    suffix = ".{}".format(name.split(".")[-1])
    tmp_input = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix)
    tmp_input.write(content)
    tmp_input.flush()

    suffix = ".source.wav"
    tmp_output = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix)

    stream = ffmpeg.input(tmp_input.name)
    stream = ffmpeg.output(
        stream, tmp_output.name, format="wav", bits_per_raw_sample=16, ac=1, ar=16000
    )
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)

    output = open(tmp_output.name, "rb")
    content = output.read()

    output.close()
    tmp_input.close()
    tmp_output.close()

    return "source.wav", content


def preprocess_audio(name, content):
    suffix = ".{}".format(name.split(".")[-1])
    tmp_input = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix)
    tmp_input.write(content)
    tmp_input.flush()

    suffix = ".source.wav"
    tmp_output = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix)

    tfm = sox.Transformer()
    tfm.set_output_format(rate=16000, bits=16, channels=1, encoding="signed-integer")
    tfm.build(tmp_input.name, tmp_output.name)

    output = open(tmp_output.name, "rb")
    content = output.read()

    output.close()
    tmp_input.close()
    tmp_output.close()

    return "source.wav", content


def create_request(total=3, backoff_factor=15, cache_dir=None):

    if cache_dir is not None:
        cache_name = os.path.join(cache_dir, "db")
        session = CachedSession(cache_name=cache_name, backend="sqlite")
    else:
        session = requests.Session()

    retries = Retry(total=total, backoff_factor=backoff_factor)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def fetch_local(url):
    path = url.replace("file://", "")
    name = "source.%s" % path.split(".")[-1]
    with open(path, "rb") as file:
        return name, file.read()


def fetch_remote(url, credential, cache_dir):
    if url.startswith("https://www.youtube.com") or url.startswith("https://vimeo.com"):
        return fetch_youtube(url)
    return fetch_any(url, credential, cache_dir)


def fetch_any(url, credential, cache_dir):
    __logger__.debug("downloading %s" % url)
    headers = {"User-Agent": "Mozilla/5.0", "Connection": "close"}
    if credential is not None and credential.type == "headers":
        headers = {**headers, **credential.content}

    request = create_request(cache_dir=cache_dir).get(url, headers=headers)
    request.raise_for_status()

    content_type = request.headers.get("Content-Type")

    if content_type is not None:
        content_type = content_type.split(";")[0]
        extension = mimetypes.guess_extension(content_type)
    else:
        parsed = urlparse(url)
        pattern = re.compile(r".(\w+)$", re.MULTILINE)
        match = pattern.search(parsed.path)
        extension = f".{match.group(1)}" if match else ".unknown"

    name = "source%s" % extension
    __logger__.debug("saving as %s" % name)

    return name, request.content


def fetch_youtube(url):
    options = {
        "format": "bestaudio",
        "outtmpl": "%(id)s.%(ext)s",
        "verbose": True,
        "postprocessors": [
            {
                "key": "MetadataFromTitle",
                "titleformat": "%(title)s",
            },
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            },
            {"key": "XAttrMetadata"},
        ],
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
        ydl.download([url])

    name = "{}.wav".format(info.get("id"))
    with open(name, "rb") as video:
        content = video.read()

    return "source.wav", content


def fetch_url(url, credential, cache_dir):
    if url.startswith("file://"):
        return fetch_local(url)
    return fetch_remote(url, credential, cache_dir)


def fetch_and_preprocess(url, credential=None, cache_dir=None):
    name, content = fetch_url(url, credential, cache_dir)

    extension = name.split(".")[-1]

    # XXX we need to properly test which are the formats we support
    if extension in ["mp4", "mov", "m4a"]:
        name, content = preprocess_video(name, content)
    elif extension in ["mp3", "wav"]:
        name, content = preprocess_audio(name, content)

    return name, content
