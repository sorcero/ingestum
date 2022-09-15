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
import pathlib

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .base import BaseTransformer
from .pdf_source_shapes_extract import Transformer as TTransformer
from .. import sources
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts shapes from a `PDF` source and returns a `Collection` of `Resource`
    documents for each.

    :param directory: Path to the directory where images will be extracted
    :type directory: str
    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    """

    class ArgumentsModel(BaseModel):
        directory: Optional[str] = None
        first_page: Optional[int] = None
        last_page: Optional[int] = None

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
        directory_name = directory.name
        if self.arguments.directory is not None:
            directory_name = self.arguments.directory

        pathlib.Path(directory_name).mkdir(parents=True, exist_ok=True)

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

        TTransformer(
            directory=directory_name,
            prefix="shape",
            first_page=first_page,
            last_page=last_page,
        ).extract(source)

        names = os.listdir(directory_name)
        names.sort()

        content = []
        for name in names:
            if not name.startswith("shape"):
                continue

            path = os.path.join(directory_name, name)
            components = name.split(".")
            # XXX for some reason these int() are not really needed?!
            pdf_context = {
                "page": int(components[2]),
                "left": int(components[3]),
                "top": int(components[4]),
                "right": int(components[5]),
                "bottom": int(components[6]),
            }
            document = documents.Resource.new_from(
                source, source_type="image", content=path, pdf_context=pdf_context
            )

            content.append(document)

        directory.cleanup()

        return documents.Collection.new_from(source, content=content)
