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
import cv2
import tempfile

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.pdfpage import PDFPage
from camelot.handlers import PDFHandler
from camelot.utils import validate_input, remove_extra
from camelot.parsers import Lattice

from .. import sources
from .. import documents
from .base import BaseTransformer
from .image_source_create_tabular_document import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts tables from a `PDF` Source and returns a `Collection` of `Tabular`
    documents for each.

    This variant uses a combination of text extraction, morphology analysis,
    and OCR techniques.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param engine: The OCR engine to use. Default is ``pytesseract``.
    :type engine: str
    :param options: Dictionary with kwargs for the underlying library
    :type options: dict
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = -1
        last_page: Optional[int] = -1
        engine: str = "pytesseract"
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
    def export(table, width, height):
        """Converts a 2D matrix into a Tabular document."""
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

    def find_tables(
        self,
        filepath,
        width,
        height,
        pages="1",
        password=None,
        flavor="lattice",
        suppress_stdout=False,
        layout_kwargs={},
        **kwargs,
    ):
        """Returns a list of Tabular documents, using OCR if necessary."""
        directory = tempfile.TemporaryDirectory()
        tempdir = directory.name
        tabular_docs = []

        # Set up Camelot
        validate_input(kwargs, flavor=flavor)
        handler = PDFHandler(filepath, pages=pages, password=password)
        kwargs = remove_extra(kwargs, flavor=flavor)
        parser = Lattice(**kwargs)

        for p in handler.pages:
            handler._save_page(handler.filepath, p, tempdir)
        pages = [tempdir + f"/page-{p}.pdf" for p in handler.pages]

        for p in pages:
            parser._generate_layout(p, layout_kwargs)
            parser.backend.convert(parser.filename, parser.imagename)
            parser._generate_table_bbox()

            for index, t_bbox in enumerate(
                sorted(parser.table_bbox.keys(), key=lambda x: x[1], reverse=True)
            ):

                # If text is found within the bounding box, no need for OCR
                found_text = False
                for obj in parser.horizontal_text:
                    if (
                        obj.bbox[0] >= t_bbox[0]
                        and obj.bbox[1] >= t_bbox[1] + (t_bbox[3] - t_bbox[1]) / 4
                        and obj.bbox[2] <= t_bbox[2]
                        and obj.bbox[3] <= t_bbox[3] - (t_bbox[3] - t_bbox[1]) / 4
                    ):
                        cols, rows, v_s, h_s = parser._generate_columns_and_rows(
                            index, t_bbox
                        )
                        table = parser._generate_table(
                            index, cols, rows, v_s=v_s, h_s=h_s
                        )
                        tabular_docs.append(self.export(table, width, height))
                        found_text = True
                        break
                if found_text:
                    continue

                # OCR table ingestion
                img = cv2.imread(parser.imagename, 1)
                img_width, img_height = img.shape[1], img.shape[0]
                pdf_width_scaler = parser.pdf_width / float(img_width)
                pdf_height_scaler = parser.pdf_height / float(img_height)

                img_left = int(t_bbox[0] / pdf_width_scaler)
                img_top = int((parser.pdf_height - t_bbox[3]) / pdf_height_scaler)
                img_right = int(t_bbox[2] / pdf_width_scaler)
                img_bottom = int((parser.pdf_height - t_bbox[1]) / pdf_height_scaler)

                pageno = int(os.path.basename(parser.rootname).replace("page-", ""))
                crop = img[img_top:img_bottom, img_left:img_right]
                crop_path = os.path.join(
                    directory.name, f"table_ocr_image_{pageno}_{index}.png"
                )
                cv2.imwrite(crop_path, crop)

                image_source = sources.Image(path=crop_path)
                process_background = (
                    kwargs["process_background"]
                    if "process_background" in kwargs
                    else False
                )
                document = TTransformer(
                    process_background=process_background,
                    engine=self.arguments.engine,
                ).transform(image_source)
                document.pdf_context = documents.resource.PDFContext(
                    left=int(t_bbox[0]),
                    top=int(parser.pdf_height - t_bbox[3]),
                    right=int(t_bbox[2]),
                    bottom=int(parser.pdf_height - t_bbox[1]),
                    page=pageno,
                )
                tabular_docs.append(document)

        directory.cleanup()
        return tabular_docs

    def extract(self, source):
        options = {}
        if self.arguments.options:
            options = self.arguments.options

        first_page = self.arguments.first_page if self.arguments.first_page > 0 else 1
        last_page = (
            self.arguments.last_page
            if self.arguments.last_page > 0
            else source.get_pages()
        )

        options["pages"] = f"{str(first_page)}-{str(last_page)}"

        if "flavor" in options and options["flavor"] != "lattice":
            raise NotImplementedError("Camelot flavor must be lattice")
        options["flavor"] = "lattice"

        width, height = self.get_size(source)
        tables = self.find_tables(source.path, width, height, **options)

        return tables

    def transform(self, source: sources.PDF) -> documents.Collection:
        super().transform(source=source)
        content = self.extract(source)
        return documents.Collection.new_from(source, content=content)
