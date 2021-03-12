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
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a XML source input into a XML document
    where the document contains the full XML.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.XML

    class OutputsModel(BaseModel):
        document: documents.XML

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, source):
        super().transform(source=source)

        with open(source.path, "r") as xml:
            content = xml.read()

        document = documents.XML.new_from(source)
        document.content = content

        return document
