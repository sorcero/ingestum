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

from pydantic import BaseModel
from typing import Optional, Union
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Tabular` document into a `Passage` document where the table is
    formatted as markdown.

    :param format: Dictionary with table headers
    :type format: dict
    """

    class ArgumentsModel(BaseModel):
        format: Union[dict, None]

    class InputsModel(BaseModel):
        document: documents.Tabular

    class OutputsModel(BaseModel):
        collection: documents.Passage

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def convert(self, table):
        text = ""

        # create a dictionary with integer string keys replaced with int keys
        format_int = {}

        if self.arguments.format is not None:
            for key in self.arguments.format:
                format_int[int(key)] = self.arguments.format[key]

        # Use format for headers if given
        if bool(format_int):
            for i, _ in enumerate(format_int):
                text += "| %s " % format_int[i]
            text += "|\n"

            for i, _ in enumerate(format_int):
                text += "| --- "
            text += "|\n"

        # Markdown table content
        for r, _ in enumerate(table):
            for c, _ in enumerate(table[r]):
                text += "| %s " % table[r][c]
            text += "|\n"

            if not bool(format_int) and r == 0:
                for c in enumerate(table[r]):
                    text += "| --- "
                text += "|\n"

        text += "|\n"

        return text

    def transform(self, document: documents.Tabular) -> documents.Passage:
        super().transform(document=document)

        return documents.Passage.new_from(
            document, content=self.convert(document.content)
        )
