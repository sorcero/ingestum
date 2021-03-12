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
from .. import documents
from .pdf_source_text_extract import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts text from a PDF Source and returns
    a collection of Text documents.

    Parameters
    ----------
    first_page : int
        First page to be used
    last_page : int
        Last page to be used
    options: dict
        Dictionary with params for the underlying library
    regexp : str
        Regular expression to filter extract text
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        regexp: Optional[str] = None

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, source):
        super().transform(source=source)

        directory = tempfile.TemporaryDirectory()
        directory_name = directory.name

        TTransformer(
            directory=directory_name,
            prefix="text",
            first_page=self.arguments.first_page,
            last_page=self.arguments.last_page,
            options=self.arguments.options,
            regexp=self.arguments.regexp,
        ).extract(source)

        names = os.listdir(directory_name)
        names.sort()

        content = []
        for name in names:
            if not name.startswith("text"):
                continue

            path = os.path.join(directory_name, name)
            with open(path) as file:
                text = file.read()

            components = name.split(".")
            pdf_context = {
                "page": components[2],
                "left": components[3],
                "top": components[4],
                "right": components[5],
                "bottom": components[6],
            }
            document = documents.Text.new_from(
                source, content=text, pdf_context=pdf_context
            )
            content.append(document)

        directory.cleanup()

        return documents.Collection.new_from(source, content=content)
