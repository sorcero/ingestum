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
    Transforms a Passage document into another Passage
    document where the content is replace by a subset
    given a regular expression.

    Parameters
    ----------
    regex : str
        Regular expression used for replacement
    """

    class ArgumentsModel(BaseModel):
        regex: str

    class InputsModel(BaseModel):
        document: documents.Passage

    class OutputsModel(BaseModel):
        document: documents.Passage

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def string_split(self, content):
        parts = re.split(self.arguments.regex, content)
        if len(parts) > 1:
            return parts[1]
        return content

    def transform(self, document):
        super().transform(document=document)

        return document.new_from(document, content=self.string_split(document.content))
