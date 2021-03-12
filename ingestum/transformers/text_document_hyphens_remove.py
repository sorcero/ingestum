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

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from ..utils import tokenize
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Text document with words separated by hyphens
    into another Text document where the hyphens are removed
    and replaced by words put back together.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: documents.Text

    class OutputsModel(BaseModel):
        document: documents.Text

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def dehyphenate(content):
        lines = content.split("\n")

        # Reset content
        content = ""

        # First, make a dictionary of words from the document.
        wlist = []
        skip_first = False
        for text in lines:
            ws = text.split()
            if len(ws) == 0:
                continue
            if ws[-1][-1] == "-":
                skip_first = True
                words = tokenize(" ".join(ws[0:-1]))
            elif skip_first:
                skip_first = False
                words = tokenize(" ".join(ws[1:]))
            else:
                words = tokenize(" ".join(ws))

            for i in range(len(words)):
                if words[i] not in wlist:
                    wlist.append(words[i])

        # Next, see if the dehypenated word is in the dictionary.
        last_word = None
        for text in lines:
            # ignore blank lines
            ws = text.split()
            if len(ws) == 0:
                content += "{}\n".format("")
                continue

            # ignore table lines
            if text[0] == "|":
                content += "{}\n".format(text)
                continue

            # are we checking for a hyphenated word?
            if last_word is not None:
                tokenized_word = tokenize(ws[0])
                if len(tokenized_word) == 0:
                    first_word = ws[0]
                else:
                    first_word = tokenized_word[0]
                dehyphenated_word = "%s%s" % (last_word, first_word)
                if dehyphenated_word in wlist:
                    ws[0] = "%s%s" % (last_word, ws[0])
                else:
                    ws[0] = "%s-%s" % (last_word, ws[0])
            if ws[-1][-1] == "-":
                last_word = ws[-1][0:-1]
                content += "{}\n".format(" ".join(ws[0:-1]))
            else:
                last_word = None
                content += "{}\n".format(" ".join(ws))

        return content

    def transform(self, document):
        super().transform(document=document)

        content = self.dehyphenate(document.content)

        return document.new_from(document, content=content)
