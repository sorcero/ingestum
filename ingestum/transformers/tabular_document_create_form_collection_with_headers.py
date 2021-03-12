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
import re

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Tabular document into a Collection document
    where each row is converted to a Form (dictionary).

    Parameters
    ----------
    headers : dict
        Pre-defined headers format
    clues: str
        Regular expression to identify other possible headers
    """

    class ArgumentsModel(BaseModel):
        headers: dict
        clues: str

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        collection: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def convert(self, document):
        forms = []

        headers = dict(self.arguments.headers)
        pattern = re.compile(self.arguments.clues, re.MULTILINE)

        for row in document.content:
            # Check if this row is a header
            is_header = next((c for c in row if pattern.search(c.strip())), None)

            # If is a header row, update the headers dict
            if is_header is not None:
                for index, cell in enumerate(row):
                    if index in self.arguments.headers:
                        continue
                    elif cell:
                        headers[index] = f"{cell.strip()}_{index}"
                    elif index not in headers:
                        headers[index] = f"Unknown_{index}"
                continue

            # If is a data row, add a new data entry
            entry = {}

            for index, cell in enumerate(row):
                header = headers.get(index, f"Unknown_{index}")
                entry[header] = cell

            forms.append(documents.Form.new_from(document, content=entry))

        return forms

    def transform(self, document):
        super().transform(document=document)

        return documents.Collection.new_from(document, content=self.convert(document))
