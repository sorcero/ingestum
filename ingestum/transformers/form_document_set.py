# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
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
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Form document into a new Form
    document with given key and value set.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: Optional[documents.Form]
        key: documents.Text
        value: documents.Text

    class OutputsModel(BaseModel):
        document: documents.Text

    type: Literal[__script__] = __script__
    arguments: Optional[ArgumentsModel]
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, document, key, value):
        super().transform(document=document, key=key, value=value)

        document = documents.Form.new_from(document)
        document.content[key.content] = value.content

        return document
