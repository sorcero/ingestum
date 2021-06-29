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
    Transforms a `Tabular` document into another `Tabular` document where rows
    are removed if these rows match a given conditional.

    :param conditional: Conditional object to be used for determining lines to remove
    :type conditional: conditionals.base.BaseConditional
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        document: documents.Tabular

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, document: documents.Tabular) -> documents.Tabular:
        super().transform(document=document)

        table = []
        content = copy.deepcopy(document.content)
        for row in content:
            if self.arguments.conditional.evaluate(row) is False:
                table.append(row)

        rows = len(table)
        columns = len(table[0]) if rows else 0

        return document.new_from(document, content=table, rows=rows, columns=columns)
