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
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")

SUPERSCRIPT = [
    "⁰",
    "¹",
    "²",
    "³",
    "⁴",
    "⁵",
    "⁶",
    "⁷",
    "⁸",
    "⁹",
    "⁺",
    "⁻",
    "⁼",
    "⁽",
    "⁾",
    "ᵃ",
    "ᵇ",
    "ᶜ",
    "ᵈ",
    "ᵉ",
    "ᶠ",
    "ᵍ",
    "ʰ",
    "ⁱ",
    "ʲ",
    "ᵏ",
    "ˡ",
    "ᵐ",
    "ⁿ",
    "ᵒ",
    "ᵖ",
    "ʳ",
    "ˢ",
    "ᵗ",
    "ᵘ",
    "ᵛ",
    "ʷ",
    "ˣ",
    "ʸ",
    "ᶻ",
    "ᴬ",
    "ᴮ",
    "ᴰ",
    "ᴱ",
    "ᴳ",
    "ᴴ",
    "ᴵ",
    "ᴶ",
    "ᴷ",
    "ᴸ",
    "ᴹ",
    "ᴺ",
    "ᴼ",
    "ᴾ",
    "ᴿ",
    "ᵀ",
    "ᵁ",
    "ⱽ",
    "ᵂ",
]
SUP = "0123456789+-=()abcdefghijklmnoprstuvwxyzABDEGHIJKLMNOPRTUVW"


def sup2superscript(text):
    """
    Parameters
    ----------
    text : str
        A single string

    Returns
    -------
    text : str
        Same text where characters are replaced by superscript unicode versions
    """
    for i in range(len(text)):
        if text[i] in SUP:
            text = text.replace(text[i], SUPERSCRIPT[SUP.index(text[i])], 1)
    return text


class Transformer(BaseTransformer):
    """
    Transforms a HTML document with sup tags into another HTML
    document where the tags are replaced by unicode characters.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: documents.HTML

    class OutputsModel(BaseModel):
        document: documents.HTML

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def replace(content):
        soup = BeautifulSoup(content, "lxml")
        for tag in soup.select("sup"):
            tag.replace_with(sup2superscript(tag.text))
        return str(soup)

    def transform(self, document):
        super().transform(document=document)

        return document.new_from(document, content=self.replace(document.content))
