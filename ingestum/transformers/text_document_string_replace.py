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

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms `Text` document into another `Text` document where text matching
    regular expression is replaced by the given replacement expression.

    :param regexp: Regular expression to find the string to be replaced
    :type regexp: str
    :param replacement: String to be used as replacement
    :type replacement: str
    """

    class ArgumentsModel(BaseModel):
        regexp: str
        replacement: str

    class InputsModel(BaseModel):
        document: documents.Text

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def replace(self, content):
        pattern = re.compile(self.arguments.regexp, re.MULTILINE)
        return pattern.sub(self.arguments.replacement, content)

    def transform(self, document: documents.Text) -> documents.Text:
        super().transform(document=document)

        content = self.replace(document.content)

        return document.new_from(document, content=content)
