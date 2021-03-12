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
import numpy as np

from pydantic import BaseModel
from typing import Optional, Union
from typing_extensions import Literal

from .. import documents
from .. import conditionals
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")
__conditionals__ = tuple(conditionals.base.BaseConditional.__subclasses__())


class Transformer(BaseTransformer):
    """
    Transforms a Tabular document into another Tabular document
    where top rows are stripped out of the original document.

    Parameters
    ----------
    condtional : Conditional
        Conditional that determines where to stop stripping rows
    transpose : bool
        Whether to transpose the table for evaluating the condition
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]
        transpose: bool = False

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        document: documents.Tabular

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, document):
        super().transform(document=document)

        table = copy.deepcopy(document.content)

        if self.arguments.transpose:
            table = np.array(table)
            table = table.transpose()
            table = table.tolist()

        strip = None
        for index, row in enumerate(table):
            if self.arguments.conditional.evaluate(row) is True:
                strip = index
                break

        table = table[strip:] if strip else table

        if self.arguments.transpose:
            table = np.array(table)
            table = table.transpose()
            table = table.tolist()

        rows = len(table)
        columns = len(table[0]) if rows else 0

        return document.new_from(document, content=table, rows=rows, columns=columns)
