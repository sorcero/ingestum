# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
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
import logging
import re
import numpy
import camelot

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.layout import LAParams, LTTextBox, LTLine, LTRect
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

from .. import sources
from .. import documents

from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts tables from a `PDF` Source using regular expression markers and
    the number of lines in the table and returns a `Collection` of `Tabular`
    documents for each.

    :param start_regexp: Regexp to identify the start of tables in the PDF text
    :type start_regexp: str
    :param num_lines: Number of horizontal lines between the start of the
        table and the next paragraph
    :type num_lines: int
    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with kwargs for the underlying library
    :type options: dict
    """

    class ArgumentsModel(BaseModel):
        start_regexp: str
        num_lines: int
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

    def combine_lines(self, lines):
        if len(lines) == 0:
            return lines

        new_lines = []
        curr = lines[0]
        for line in lines:
            if line["y"] == curr["y"]:
                if line["x2"] > curr["x2"]:
                    curr["x2"] = line["x2"]
            else:
                new_lines.append(curr)
                curr = line
        new_lines.append(curr)
        return new_lines

    def find_coords(self, layout, pageno):
        tables = []

        start_regexp = re.compile(self.arguments.start_regexp)
        starts = []
        h_lines = []

        for lobj in layout:
            if isinstance(lobj, LTTextBox) and start_regexp.search(lobj.get_text()):
                coords = {"page": pageno, "y": str(lobj.bbox[1])}
                starts.append(coords)

            if isinstance(lobj, LTLine) and lobj.bbox[1] == lobj.bbox[3]:
                coords = {
                    "page": pageno,
                    "x1": str(lobj.bbox[0]),
                    "x2": str(lobj.bbox[2]),
                    "y": str(lobj.bbox[3]),
                }
                h_lines.append(coords)

            # Some PDFs use really thin rectangles (height < 1) instead of
            # line objects to represent lines.
            if isinstance(lobj, LTRect) and lobj.bbox[3] - lobj.bbox[1] < 1:
                coords = {
                    "page": pageno,
                    "x1": str(lobj.bbox[0]),
                    "x2": str(lobj.bbox[2]),
                    "y": str((lobj.bbox[1] + lobj.bbox[3]) / 2),
                }
                h_lines.append(coords)

        h_lines = sorted(h_lines, key=lambda i: float(i["y"]), reverse=True)
        h_lines = self.combine_lines(h_lines)

        for start in starts:
            count = self.arguments.num_lines
            for line in h_lines:
                if float(line["y"]) < float(start["y"]):
                    count -= 1
                if count == 0:
                    table_coords = {
                        "page": pageno,
                        "x1": line["x1"],
                        "y1": start["y"],
                        "x2": line["x2"],
                        "y2": line["y"],
                    }
                    tables.append(table_coords)
                    break

        return tables

    def find_tables(self, source):
        first_page = self.arguments.first_page
        if first_page is None:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None:
            last_page = source.get_pages()

        # Set up PDFMiner objects
        manager = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(manager, laparams=laparams)
        interpreter = PDFPageInterpreter(manager, device)

        pagenos = set([x - 1 for x in range(first_page, last_page + 1)])
        pdf = open(source.path, "rb")
        pages = PDFPage.get_pages(
            pdf, pagenos=pagenos, caching=True, check_extractable=False
        )

        tables = []

        for pageno, page in enumerate(pages, start=first_page):
            interpreter.process_page(page)
            layout = device.get_result()

            tables += self.find_coords(layout, pageno)

        pdf.close()
        return tables

    @staticmethod
    def export(table, width, height):
        content = []

        def cleanup(text):
            text = text.replace("\n", " ")
            text = text.strip()
            return text

        for row in table.cells:
            content.append([cleanup(cell.text) for cell in row])

        # XXX Increases bounding box by 2px on each side to more easily replace
        # text in PDFSourceCreateTextDocumentReplacedExtractables.
        pdf_context = {
            "left": int(table.cells[0][0].lt[0]) - 2,
            "top": height - int(table.cells[0][0].lt[1]) - 2,
            "right": int(table.cells[-1][-1].rb[0]) + 2,
            "bottom": height - int(table.cells[-1][-1].rb[1]) + 2,
            "page": int(table.page),
        }

        rows = len(content)
        columns = len(content[0]) if content else 0

        document = documents.Tabular.new_from(
            None, content=content, rows=rows, columns=columns, pdf_context=pdf_context
        )

        return document.dict()

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
        tabular_docs = []

        options = {}
        if self.arguments.options:
            options = self.arguments.options

        if not "flavor" in options:
            options["flavor"] = "stream"

        tables = self.find_tables(source)
        width, height = self.get_size(source)

        for index, table in enumerate(tables):
            coords = [table["x1"], table["y1"], table["x2"], table["y2"]]
            coords = ",".join(coords)
            options["table_areas"] = [coords]

            options["pages"] = str(table["page"])

            # XXX Camelot throws an exception if no tables found when using
            # table_areas
            try:
                _tables = camelot.read_pdf(str(source.path), **options)
            except ValueError as e:
                __logger__.debug(
                    str(e),
                    extra={
                        "props": {
                            "transformer": self.type,
                            "pageno": table["page"],
                            "x1": table["x1"],
                            "y1": height - table["y1"],
                            "x2": table["x2"],
                            "y2": height - table["y2"],
                        }
                    },
                )
                _tables = []

            _tables = list(_tables)
            _tables.sort(key=lambda table: self.discretize(table, width, height))

            for _table in _tables:
                tabular_docs.append(self.export(_table, width, height))

            options.pop("table_areas")

        return tabular_docs

    def transform(self, source: sources.PDF) -> documents.Collection:
        super().transform(source=source)
        content = self.extract(source)
        return documents.Collection.new_from(source, content=content)
