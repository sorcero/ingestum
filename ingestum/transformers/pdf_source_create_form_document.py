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
from typing import Optional
from typing_extensions import Literal

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSLiteral, literal_name

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transform a PDF source input into a Form document
    where AcroForm fields are dumped into a generic
    python dictionary.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Form

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def extract(source):
        form = {}
        pdf = open(source.path, "rb")
        parser = PDFParser(pdf)
        document = PDFDocument(parser)

        for field in resolve1(document.catalog["AcroForm"])["Fields"]:
            field = resolve1(field)
            key = source.decode(field.get("T"))
            value = field.get("V")

            if isinstance(value, PSLiteral):
                value = literal_name(value)
            elif value and not isinstance(value, str):
                value = source.decode(value)

            form[key] = value

        pdf.close()
        return form

    def transform(self, source):
        super().transform(source=source)

        return documents.Form.new_from(source, content=self.extract(source))
