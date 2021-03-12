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
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Tabular document into a collection of Form documents
    where each row cell is turned into a key value
    given a format dictionary.

    Parameters
    ----------
    format : dict
        Format dictionary with columns labels for each index
    """

    class ArgumentsModel(BaseModel):
        format: dict

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        collection: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, document):
        super().transform(document=document)

        # create a dictionary with integer string keys replaced with int keys
        format_int = {}
        for key in self.arguments.format:
            format_int[int(key)] = self.arguments.format[key]

        content = []
        for row in document.content:
            form = {}
            for index, value in enumerate(row):
                form[format_int[index]] = value
            content.append(documents.Form.new_from(document, content=form))

        return documents.Collection.new_from(document, content=content)
