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

from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `HTML` source input into a `HTML` document where the document
    contains the full HTML.

    :param target: Target element or classes to limit the contet to a subset
    :type target: str
    """

    class ArgumentsModel(BaseModel):
        target: Optional[str]

    class InputsModel(BaseModel):
        source: sources.HTML

    class OutputsModel(BaseModel):
        document: documents.HTML

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def extract(self, html):
        soup = BeautifulSoup(html, "lxml")
        element = None

        if self.arguments.target:
            element = soup.find(self.arguments.target)
        if self.arguments.target and element is None:
            element = soup.select_one(self.arguments.target)
        if element is None:
            element = soup

        return str(element)

    def transform(self, source: sources.HTML) -> documents.HTML:
        super().transform(source=source)

        with open(source.path) as html:
            content = self.extract(html.read())

        return documents.HTML.new_from(source, content=content)
