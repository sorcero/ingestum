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
import csv

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a CSV input source into a CSV document.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.CSV

    class OutputsModel(BaseModel):
        document: documents.CSV

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def extract_text(source):
        file = open(source.path)
        table = csv.reader(file)
        rows = []
        for row in table:
            cells = []
            for cell in row:
                cell = cell.replace(sources.csv.SEPARATOR, "")
                cell = cell.replace(sources.csv.BOUND, "")
                cell = cell.replace(sources.csv.EOL, " ")
                cell = sources.csv.BOUND + cell + sources.csv.BOUND
                cells.append(cell)
            rows.append(sources.csv.SEPARATOR.join(cells))
        file.close()
        return sources.csv.EOL.join(rows)

    def transform(self, source):
        super().transform(source=source)

        return documents.CSV.new_from(source, content=self.extract_text(source))
