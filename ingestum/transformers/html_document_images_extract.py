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
import requests
import pathlib

from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `HTML` document with img tags into another `HTML` document
    where the tags are replaced by references to the downloaded versions of
    these images, in follow format ``file:///image.png``.

    :param directory: Path to the directory where images will be extracted
    :type directory: str
    :param url: Absolute url component to the image
    :type url: str
    """

    class ArgumentsModel(BaseModel):
        directory: str
        url: Optional[str]

    class InputsModel(BaseModel):
        document: documents.HTML

    class OutputsModel(BaseModel):
        document: documents.HTML

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def fetch(self, url):
        request = requests.get(url)

        pathlib.Path(self.arguments.directory).mkdir(parents=True, exist_ok=True)

        name = os.path.basename(urlparse(url).path)
        path = os.path.join(self.arguments.directory, name)
        with open(path, "wb") as file:
            file.write(request.content)

        return "[file:///{}]".format(name)

    def replace(self, content):
        soup = BeautifulSoup(content, "lxml")

        for tag in soup.select("img"):
            src = urlparse(tag.get("src"))
            if src.scheme == "data":
                continue
            # XXX we don't support downloading assets from file://
            url = urlparse(self.arguments.url)
            if url.scheme == "file":
                continue
            if self.arguments.url:
                tag["src"] = urljoin(self.arguments.url, tag.get("src"))
            if src.scheme:
                tag.replace_with(self.fetch(tag.get("src")))

        return str(soup)

    def transform(self, document: documents.HTML) -> documents.HTML:
        super().transform(document=document)

        _document = document.new_from(document)

        _document.content = self.replace(document.content)

        return _document
