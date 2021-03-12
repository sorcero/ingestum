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

from pdf2image import convert_from_path
from pytesseract.pytesseract import image_to_string

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a PDF input source into a Text document where
    the Text document contains all human-readable text from
    the PDF, using OCR techniques.

    Parameters
    ----------
    first_page : int
        First page to be used
    last_page : int
        Last page to be used
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Text

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def extract(self, source):
        text = ""
        pdf = open(source.path, "rb")
        directory = tempfile.TemporaryDirectory()

        first_page = self.arguments.first_page
        if first_page is None:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None:
            last_page = source.get_pages()

        text = ""
        for page in range(first_page, last_page + 1):
            path = convert_from_path(
                source.path,
                first_page=page,
                last_page=page,
                output_folder=directory.name,
                paths_only=True,
            )[0]
            prefix = "\n" if page > 1 else ""
            text += f"{prefix}{image_to_string(path).strip()}"
            os.remove(path)

        directory.cleanup()
        pdf.close()
        return text

    def transform(self, source):
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
