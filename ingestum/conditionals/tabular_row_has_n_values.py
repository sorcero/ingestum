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

from typing import List
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .base import BaseConditional

__script__ = os.path.basename(__file__).replace(".py", "")


class Conditional(BaseConditional):
    """
    Is the row made only of values on specific positions?

    Parameters
    ----------
    columns : list
        A list of indexes for the target columns
    """

    class ArgumentsModel(BaseModel):
        columns: List[int]

    class InputsModel(BaseModel):
        row: List[str]

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]

    def evaluate(self, row):
        super().evaluate(row=row)

        length = len(row)
        total_empty = len(list((value for value in row if not value)))

        if (total_empty + len(self.arguments.columns)) != length:
            return False

        for index in self.arguments.columns:
            if not row[index]:
                return False

        return True
