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
import csv
import tempfile

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `CSV` input source into a `Tabular` document.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.CSV

    class OutputsModel(BaseModel):
        document: documents.Tabular

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    @staticmethod
    def extract_text(source):
        with open(source.path) as file:
            return file.read()

    def transform(self, source: sources.CSV) -> documents.Tabular:
        super().transform(source=source)

        content = self.extract_text(source)

        # XXX better way to deal with universal-newline-mode?
        dump_file = tempfile.NamedTemporaryFile(mode="w")
        dump_file.write(content)
        dump_file.flush()

        with open(dump_file.name) as csv_file:
            table = [row for row in csv.reader(csv_file)]

        dump_file.close()

        rows = len(table)
        columns = len(table[0]) if rows else 0

        return documents.Tabular.new_from(
            source, content=table, rows=rows, columns=columns
        )
