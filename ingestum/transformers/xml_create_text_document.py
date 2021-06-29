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
import html

from bs4 import BeautifulSoup
from bs4.element import Comment
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `XML` document into a `Text` document where all the XML tags
    are removed and only human-readable text is preserved.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: documents.XML

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    # kudos to https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
    def tag_visible(self, element):
        if element.parent.name in [
            "style",
            "script",
            "head",
            "meta",
            "[document]",
            "noscript",
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def extract(self, xml):
        text = ""
        soup = BeautifulSoup(xml, "xml")
        elements = soup.find_all(text=True)
        elements = filter(self.tag_visible, elements)

        for element in elements:
            text += "{}".format(element)

        return html.unescape(text)

    def transform(self, document: documents.XML) -> documents.Text:
        super().transform(document=document)

        return documents.Text.new_from(document, content=self.extract(document.content))
