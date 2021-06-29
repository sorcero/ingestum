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
import pyexcel

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")

SEPARATOR = ","
EOL = "\n"
BOUND = '"'


class Transformer(BaseTransformer):
    """
    Transforms a `XLS` source input into a `CSV` document where the XLS rows are
    converted into CSV rows.

    :param sheet: Name of the sheet to access
    :type sheet: str
    """

    class ArgumentsModel(BaseModel):
        sheet: str

    class InputsModel(BaseModel):
        source: sources.XLS

    class OutputsModel(BaseModel):
        document: documents.CSV

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def extract_text(self, source):
        texts = []
        book = pyexcel.get_book(file_name=str(source.path))

        if self.arguments.sheet is not None:
            worksheet = book.sheet_by_name(self.arguments.sheet)
        else:
            worksheet = book.sheet_by_index(0)

        for row in worksheet:
            values = []
            for cell in row:
                value = cell if cell else ""
                value = str(value)
                value = value.replace(EOL, "")
                value = value.replace(SEPARATOR, "")
                value = value.replace(BOUND, "")
                value = "%s%s%s" % (BOUND, value, BOUND)
                values.append(value)
            texts.append(SEPARATOR.join(values))

        return EOL.join(texts)

    def transform(self, source: sources.XLS) -> documents.CSV:
        super().transform(source=source)

        titles = [
            source.get_metadata().get("title", ""),
            self.arguments.sheet,
        ]
        title = "-".join([t for t in titles if t])

        return documents.CSV.new_from(
            None, title=title, content=self.extract_text(source)
        )
