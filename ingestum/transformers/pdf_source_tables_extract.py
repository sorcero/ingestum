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
import numpy
import camelot

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.pdfpage import PDFPage

from .. import sources
from .. import documents

from .base import BaseTransformer
from ..utils import write_document_to_path

__script__ = os.path.basename(__file__).replace(".py", "")


class WrongOutputFormat(Exception):
    pass


class Transformer(BaseTransformer):
    """
    Extracts tables from a `PDF` source to a given output directory, to a given
    format.

    :param directory: Path to the directory where images will be extracted
    :type directory: str
    :param prefix: Prefix string used to name each extracted image
    :type prefix: str
    :param output: Output format to be used, ``json`` or ``csv``
    :type output: str
    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with kwargs for the underlying library
    :type options: dict
    """

    class ArgumentsModel(BaseModel):
        directory: Optional[str] = None
        prefix: str
        output: str
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

    @staticmethod
    def export(path, table, width, height):
        content = []

        def cleanup(text):
            text = text.replace("\n", " ")
            text = text.strip()
            return text

        for row in table.cells:
            content.append([cleanup(cell.text) for cell in row])

        pdf_context = {
            "left": int(table.cells[0][0].lt[0]),
            "top": height - int(table.cells[0][0].lt[1]),
            "right": int(table.cells[-1][-1].rb[0]),
            "bottom": height - int(table.cells[-1][-1].rb[1]),
            "page": int(table.page),
        }

        rows = len(content)
        columns = len(content[0]) if content else 0

        document = documents.Tabular.new_from(
            None, content=content, rows=rows, columns=columns, pdf_context=pdf_context
        )

        write_document_to_path(document, path)

    @staticmethod
    def get_size(source):
        pdf = open(source.path, "rb")

        pages = PDFPage.get_pages(
            pdf, pagenos=None, caching=True, check_extractable=False
        )
        page = list(pages)[0]

        width = page.mediabox[2]
        height = page.mediabox[3]

        pdf.close()
        return (width, height)

    @staticmethod
    def discretize(table, width, height):
        # XXX assumes a max of 6 columns
        bins = [20, 40, 50, 60, 80, 100]

        point = table.cells[0][0].lt
        point = [(point[0] / width) * 100, ((height - point[1]) / height) * 100]

        point = numpy.digitize(list(point), bins)
        point = (table.page, bins[point[0]], bins[point[1]])

        return point

    def extract(self, source):
        options = {}
        if self.arguments.options:
            options = self.arguments.options

        first_page = self.arguments.first_page
        if first_page is None:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None:
            last_page = source.get_pages()

        options["pages"] = "%d-%d" % (first_page, last_page)
        tables = camelot.read_pdf(str(source.path), **options)

        width, height = self.get_size(source)
        tables = list(tables)
        tables.sort(key=lambda table: self.discretize(table, width, height))

        for index, table in enumerate(tables):
            options = {}
            if self.arguments.output == "json":
                options["orient"] = "index"
                options["indent"] = 4

            path = os.path.join(
                self.arguments.directory,
                "%s.%06d.%s" % (self.arguments.prefix, index, self.arguments.output),
            )

            if self.arguments.output == "json":
                table.to_json(path, **options)
            elif self.arguments.output == "csv":
                table.to_csv(path, **options)
            elif self.arguments.output == "tabular":
                self.export(path, table, width, height)
            else:
                raise WrongOutputFormat()

    def transform(self, source: sources.PDF) -> documents.Collection:
        super().transform(source=source)

        self.extract(source)

        return source
