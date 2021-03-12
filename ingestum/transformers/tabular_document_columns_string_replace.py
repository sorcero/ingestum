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
    Transforms a Tabular document into another Tabular document
    where a column text is replaced by a given expression and
    replacement.

    Parameters
    ----------
    column : int
        Column that contains the incumbent string
    expression : str
        Expression to find the text to be replaced
    replacement : str
        String to be used as replacement
    """

    class ArgumentsModel(BaseModel):
        column: int
        expression: str
        replacement: str

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        document: documents.Tabular

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def replace(self, cell):
        return cell.replace(self.arguments.expression, self.arguments.replacement)

    def transform(self, document):
        super().transform(document=document)

        table = []
        content = copy.deepcopy(document.content)
        for row in content:
            row[self.arguments.column] = self.replace(row[self.arguments.column])
            table.append(row)

        rows = len(table)
        columns = len(table[0]) if rows else 0

        return document.new_from(document, content=table, rows=rows, columns=columns)
