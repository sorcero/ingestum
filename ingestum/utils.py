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
from typing import Any, Callable, Tuple
import requests
import logging
import time

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from json.decoder import JSONDecodeError
from nltk.tokenize import RegexpTokenizer

from requests_cache import CachedSession
from datetime import datetime
from string import punctuation

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


def get_document_from_dict(document_dict):
    """
    Creates an Ingestum Document instance from the document's dictionary
    representation (JSON) and returns it.

    :param document_dict: Ingestum document's dictionary representation
    :type document_dict: dict

    :return: Ingestum Document instance
    :rtype: documents.base.BaseDocument
    """

    from pydantic import BaseModel
    from typing import Union
    from . import documents

    class Parser(BaseModel):
        document: Union[tuple(find_subclasses(documents.base.BaseDocument))]

    parsed = Parser(document=document_dict)

    return parsed.document


def get_document_from_path(path):
    """
    Parses an Ingestum document's JSON file and generates an Ingestum Document
    instance from it.

    :param path: Path to the JSON document file
    :type path: string

    :return: Ingestum Document instance
    :rtype: documents.base.BaseDocument
    """

    with open(path) as json_file:
        document = json.loads(json_file.read())

    return get_document_from_dict(document)


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


def date_string_from_xml_node(node, y="Year", m="Month", d="Day"):
    string = ""

    if year := node.find(y):
        string += year.text
        if month := node.find(m):
            string += f"-{month.text}"
            if day := node.find(d):
                string += f"-{day.text}"

    return string


def date_from_string(string: str) -> datetime.date:
    known_formats = [
        "%Y-%b-%d",
        "%Y-%b-%-d",
        "%Y-%m-%d",
        "%Y-%-m-%d",
        "%Y-%m-%-d",
        "%Y-%-m-%-d",
        "%Y-%b",
        "%Y-%m",
        "%Y-%-m",
        "%Y",
    ]
    for known_format in known_formats:
        try:
            return datetime.strptime(string, known_format).date()
        except ValueError:
            pass
    raise Exception("No valid date format found")


def date_to_default_format(date: datetime.date) -> str:
    return date.isoformat()


def stringify_document(document):
    return json.dumps(document.dict(), indent=4, sort_keys=True, ensure_ascii=False)


def write_document_to_path(document, path):
    with open(path, "w") as document_file:
        document_file.write(stringify_document(document))


def sanitize_string(string):
    return string.strip(punctuation).strip()


def calculate_runtime(
    run_func: Callable, print_time: bool = False, label: str = None
) -> Tuple[int, Any]:
    """
    Calculates and prints the time in milliseconds to run a function

    :param run_func: Function whose run time is to be determined
    :type run_func: function
    :param print_time: Whether to print the run time
    :type print_time: bool
    :param label: Label for print
    :type label: str

    :return: Tuple of the run time in milliseconds and output returned by the function
    :rtype: tuple(int, Any)
    """

    init_time = time.time() * 1000

    output = run_func()

    last_time = time.time() * 1000
    time_run = last_time - init_time

    if print_time:
        if label is not None:
            print(f"\n{label}: {str(time_run)} ms\n")
        else:
            print(f"\nrun time: {str(time_run)} ms\n")

    return time_run, output
