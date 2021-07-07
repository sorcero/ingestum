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
import json
import requests
import logging

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
