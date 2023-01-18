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
import time
import requests
import logging

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


class GlobalTimeOut(object):
    def __init__(self, default_timeout=None):
        self.default_timeout = default_timeout

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", self.default_timeout)
        return super().request(*args, **kwargs)


class TimedOutSession(GlobalTimeOut, requests.Session):
    def __init__(self, default_timeout=None, *args, **kargs):
        GlobalTimeOut.__init__(self, default_timeout)
        requests.Session.__init__(self, *args, **kargs)


class TimedOutCachedSession(GlobalTimeOut, CachedSession):
    def __init__(self, default_timeout=None, *args, **kargs):
        GlobalTimeOut.__init__(self, default_timeout)
        CachedSession.__init__(self, *args, **kargs)


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


def retry(attempts, backoff, errors):
    def decorator(function):
        def wrapper(*args, **kargs):
            for attempt in range(0, attempts):
                try:
                    return function(*args, **kargs)
                except errors as e:
                    if attempt + 1 == attempts:
                        raise e
                    delay = backoff * (2 ** attempt)
                    __logger__.warning(
                        "retrying",
                        extra={
                            "props": {
                                "decorated": str(function),
                                "error": str(e),
                                "attempt": f"{attempt + 1}/{attempts}",
                                "delay": delay,
                            }
                        },
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


def create_request(
    total=3,
    backoff_factor=15,
    cache_dir=None,
    status_forcelist=None,
    allowed_methods=None,
    default_timeout=3600,
):
    if cache_dir is not None:
        cache_name = os.path.join(cache_dir, "db")
        session = TimedOutCachedSession(
            cache_name=cache_name,
            backend="sqlite",
            default_timeout=default_timeout,
        )
    else:
        session = TimedOutSession(
            default_timeout=default_timeout,
        )

    kargs = {
        "total": total,
        "backoff_factor": backoff_factor,
    }

    if status_forcelist is not None:
        kargs["status_forcelist"] = status_forcelist
    if allowed_methods is not None:
        kargs["allowed_methods"] = allowed_methods

    retries = Retry(**kargs)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def date_string_from_xml_node(node, y="Year", m="Month", d="Day"):
    string = ""

    if year := node.find(y):
        string += year.text.strip()
        if month := node.find(m):
            string += f"-{month.text.strip()}"
            if day := node.find(d):
                string += f"-{day.text.strip()}"

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
    raise Exception(f"No valid date format found for {string}")


def date_to_default_format(date: datetime.date) -> str:
    return date.isoformat()


def stringify_document(document, formatted=True):
    params = {}

    if formatted is True:
        params = {
            "indent": 4,
            "sort_keys": True,
        }

    return json.dumps(document.dict(), ensure_ascii=False, **params)


def write_document_to_path(document, path, formatted=True):
    with open(path, "w") as document_file:
        document_file.write(stringify_document(document, formatted=formatted))


def sanitize_string(string):
    return string.strip(punctuation).strip()


def html_table_to_markdown_table(node):
    text = ""

    # extract tabular document
    if node.thead is not None:
        headers = node.thead.find_all("tr")
        lines = "|"
        for header in headers:
            columns = header.find_all("th")
            for cell in columns:
                text += "| %s " % cell.text.strip()
                lines += "---|"
            text += "|\n"
        lines += "\n"
        text += lines

    if node.thead is None and node.tbody is not None:
        row = node.tbody.find("tr")
        n_columns = len(row.find_all("td"))
        lines = "|"
        for i in range(n_columns):
            text += "|  "
            lines += "---|"
        text += "|\n"
        lines += "\n"
        text += lines

    if node.tbody is not None:
        rows = node.tbody.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            for cell in columns:
                text += "| %s " % cell.text.strip()
            text += "|\n"
        text += "|"

    return text
