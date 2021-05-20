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
from typing import Optional, Union
from typing_extensions import Literal

from .. import documents
from .. import conditionals
from .base import BaseTransformer
from ..utils import find_subclasses

__script__ = os.path.basename(__file__).replace(".py", "")
__conditionals__ = tuple(find_subclasses(conditionals.base.BaseConditional))


class Transformer(BaseTransformer):
    """
    Transforms a Tabular document into another
    Tabular document where consecutive rows are
    merged into one if the row matches a given
    condition.

    Parameters
    ----------
    conditional : Conditional
        Conditional object to be used to determine which rows to merge
    reverse : bool
        Whether it should traverse from bottom to top
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]
        reverse: bool = False

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        document: documents.Tabular

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def merge(l_row, r_row):
        return ["%s %s" % (l_row[i], r_row[i]) for i in range(0, len(l_row))]

    def transform(self, document):
        super().transform(document=document)

        table = []
        content = copy.deepcopy(document.content)
        if self.arguments.reverse:
            content = reversed(content)

        for row in content:
            if self.arguments.conditional.evaluate(row):
                if table:
                    table[-1] = self.merge(table[-1], row)
                else:
                    table.append(row)
                continue
            table.append(row)

        if self.arguments.reverse:
            table.reverse()

        rows = len(table)
        columns = len(table[0]) if rows else 0

        return document.new_from(document, content=table, rows=rows, columns=columns)
