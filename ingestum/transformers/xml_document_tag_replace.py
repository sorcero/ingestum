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
import copy
import logging

from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a XML document into another XML document
    where a given tag is replaced by a string, given a
    string format.

    The string format can take any {attribute} where:
    * {attribute} is an actual tag attribute
    * {@text} to replace with the tag text content
    * {@tag} to replace it with the tag

    Examples:
    ---------
    * "{@tag}" will result in the exact same XML.
    * "BEFORE{@tag}"
    * "{@tag}AFTER"
    * etc

    :param tag: Target XML tag
    :type tag: str
    :param replacement: Format str with Tag attributes
    :type replacement: str
    """

    class ArgumentsModel(BaseModel):
        tag: str
        replacement: str

    class InputsModel(BaseModel):
        document: documents.XML

    class OutputsModel(BaseModel):
        document: documents.XML

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def replace(self, xml):
        soup = BeautifulSoup(xml, "xml")

        for tag in soup.select(self.arguments.tag, text=True):
            try:
                data = copy.copy(tag.attrs)
                data["@text"] = tag.text

                if "{@tag}" in self.arguments.replacement:
                    pre_format, pos_format = self.arguments.replacement.split("{@tag}")
                    pre = pre_format.format(**data)
                    pos = pos_format.format(**data)
                    tag.insert_before(pre)
                    tag.insert_after(pos)
                else:
                    replacement = self.arguments.replacement.format(**data)
                    tag.insert_after(replacement)
                    tag.extract()
            except KeyError as e:
                __logger__.error(str(e), extra={"props": {"transformer": self.type}})
                pass

        return str(soup)

    def transform(self, document):
        super().transform(document=document)

        return document.new_from(document, content=self.replace(document.content))
