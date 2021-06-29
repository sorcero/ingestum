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

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Tabular` document into another `Tabular` document where
    columns are deleted or added such that the result has the specified number
    of columns.

    :param columns: Number of columns to which the Tabular document should fit
    :type columns: int
    """

    class ArgumentsModel(BaseModel):
        columns: int

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        collection: documents.Tabular

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, document: documents.Tabular) -> documents.Tabular:
        super().transform(document=document)

        table = []
        columns = self.arguments.columns
        content = copy.deepcopy(document.content)
        for row in content:
            row = row[:columns] + [""] * (columns - len(row))
            table.append(row)

        rows = len(table)
        columns = len(table[0]) if rows else 0

        return document.new_from(document, content=table, rows=rows, columns=columns)
