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
import tempfile

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .base import BaseTransformer
from .. import sources
from .. import transformers
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts tables from a `PDF` Source and returns a `Collection` of `Tabular`
    documents for each.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with kwargs for the underlying library
    :type options: dict
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, source: sources.PDF) -> documents.Collection:
        super().transform(source=source)

        directory = tempfile.TemporaryDirectory()

        first_page = (
            self.arguments.first_page
            if self.arguments.first_page is not None and self.arguments.first_page > 0
            else 1
        )
        last_page = (
            self.arguments.last_page
            if self.arguments.last_page is not None and self.arguments.last_page > 0
            else source.get_pages()
        )

        transformers.PDFSourceTablesExtract(
            directory=directory.name,
            prefix="table",
            output="tabular",
            first_page=first_page,
            last_page=last_page,
            options=self.arguments.options,
        ).extract(source)

        names = os.listdir(directory.name)
        names.sort()

        content = []
        for name in names:
            path = os.path.join(directory.name, name)
            document = documents.Tabular.parse_file(path)
            content.append(document)

        directory.cleanup()

        return documents.Collection.new_from(source, content=content)
