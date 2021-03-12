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
import math

from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Tabular document into another Tabular document
    where a given cell is augmented with content from extractables.

    Parameters
    ----------
    columns : list
        The columns that should be updated
    regexp : str
        Expression to identify the row
    """

    class ArgumentsModel(BaseModel):
        columns: List[int]
        regexp: str

    class InputsModel(BaseModel):
        collection: documents.Collection
        extractables: documents.Collection

    class OutputsModel(BaseModel):
        collection: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._pattern = re.compile(self.arguments.regexp, re.MULTILINE)

    def find_page(self, pdf_context):
        if pdf_context is None:
            return math.inf

        page = pdf_context.page
        if page is None:
            return math.inf

        return page

    def update_row(self, row, document, extractables):
        pdf_context = document.pdf_context
        if pdf_context is None:
            pdf_context = {}

        page = pdf_context.page
        if page is None:
            return

        extractable = next(
            (e for e in extractables.content if self.find_page(e.pdf_context) >= page),
            None,
        )
        if extractable is None:
            return

        for column in self.arguments.columns:
            document.content[row][column] += "\n\n" + extractable.content

    def update_table(self, document, extractables):
        for r, row in enumerate(document.content):
            match = next((c for c in row if self._pattern.search(c)), None)
            if match is not None:
                self.update_row(r, document, extractables)

    def transform(self, collection, extractables):
        super().transform(collection=collection, extractables=extractables)

        _collection = collection.new_from(collection)

        for document in _collection.content:
            self.update_table(document, extractables)

        return _collection
