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


import json
import unittest
import os
import shutil

from ingestum import documents
from ingestum import sources
from ingestum import transformers


class PDFTestCase(unittest.TestCase):

    pdf_form = sources.PDF(path="tests/data/form.pdf")
    pdf_source = sources.PDF(path="tests/data/test.pdf")
    pdf_header_and_footer = sources.PDF(path="tests/data/header_and_footer.pdf")
    pdf_tabular_collection_document = documents.Collection.parse_file(
        "tests/input/pdf_tabular_collection_document.json"
    )
    pdf_tabular_collection_document_md = documents.Collection.parse_file(
        "tests/input/pdf_tabular_collection_document_md.json"
    )

    def setUp(self):
        os.mkdir("/tmp/ingestum")

    def tearDown(self):
        shutil.rmtree("/tmp/ingestum")

    def get_expected(self, transformer):
        filepath = "tests/output/" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_pdf_source_create_form_document(self):
        document = transformers.PDFSourceCreateFormDocument().transform(
            source=self.pdf_form
        )
        self.assertEqual(
            document.dict(), self.get_expected("pdf_source_create_form_document")
        )

    def test_pdf_source_create_text_document(self):
        document = transformers.PDFSourceCreateTextDocument(
            first_page=1, last_page=3
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(), self.get_expected("pdf_source_create_text_document")
        )

    def test_pdf_source_create_text_document_no_pages(self):
        document = transformers.PDFSourceCreateTextDocument().transform(
            source=self.pdf_source
        )
        self.assertEqual(
            document.dict(), self.get_expected("pdf_source_create_text_document")
        )

    def test_pdf_source_create_text_document_ocr(self):
        document = transformers.PDFSourceCreateTextDocumentOCR(
            first_page=1, last_page=3
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(), self.get_expected("pdf_source_create_text_document_ocr")
        )

    def test_pdf_source_create_text_document_ocr_no_pages(self):
        document = transformers.PDFSourceCreateTextDocumentOCR().transform(
            source=self.pdf_source
        )
        self.assertEqual(
            document.dict(), self.get_expected("pdf_source_create_text_document_ocr")
        )

    def test_pdf_source_create_tabular_collection_document(self):
        document = transformers.PDFSourceCreateTabularCollectionDocument(
            first_page=1, last_page=3, options={"line_scale": 50}
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_create_tabular_collection_document"),
        )

    def test_pdf_source_create_tabular_collection_document_no_pages(self):
        document = transformers.PDFSourceCreateTabularCollectionDocument(
            options={"line_scale": 50}
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_create_tabular_collection_document"),
        )

    def test_pdf_source_images_create_resource_collection_document(self):
        document = transformers.PDFSourceImagesCreateResourceCollectionDocument(
            directory="/tmp/ingestum", first_page=1, last_page=3
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_images_create_resource_collection_document"),
        )

    def test_pdf_source_images_create_resource_collection_document_no_pages(self):
        document = transformers.PDFSourceImagesCreateResourceCollectionDocument(
            directory="/tmp/ingestum", first_page=1, last_page=3
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_images_create_resource_collection_document"),
        )

    def test_pdf_source_shapes_create_resource_collection_document_no_pages(self):
        document = transformers.PDFSourceShapesCreateResourceCollectionDocument(
            directory="/tmp/ingestum"
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_shapes_create_resource_collection_document"),
        )

    def test_pdf_source_text_create_text_collection_document(self):
        document = transformers.PDFSourceTextCreateTextCollectionDocument(
            first_page=1,
            last_page=3,
            options={"line_margin": 0.60},
            regexp=r"Lorem((.)*)amet",
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_text_create_text_collection_document"),
        )

    def test_pdf_source_text_create_text_collection_document_no_pages(self):
        document = transformers.PDFSourceTextCreateTextCollectionDocument(
            options={"line_margin": 0.60},
            regexp=r"Lorem((.)*)amet",
        ).transform(source=self.pdf_source)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_text_create_text_collection_document"),
        )

    def test_pdf_source_create_text_document_replaced_extractables(self):
        document = transformers.PDFSourceCreateTextDocumentReplacedExtractables(
            first_page=1, last_page=3
        ).transform(
            source=self.pdf_source,
            collection=self.pdf_tabular_collection_document,
            replacements=self.pdf_tabular_collection_document_md,
        )
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_create_text_document_replaced_extractables"),
        )

    def test_pdf_source_create_text_document_replaced_extractables_no_pages(self):
        document = (
            transformers.PDFSourceCreateTextDocumentReplacedExtractables().transform(
                source=self.pdf_source,
                collection=self.pdf_tabular_collection_document,
                replacements=self.pdf_tabular_collection_document_md,
            )
        )
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_create_text_document_replaced_extractables"),
        )

    def test_pdf_source_crop_create_image_source(self):
        transformers.PDFSourceCropCreateImageSource(
            directory="/tmp/ingestum",
            prefix="",
            page=1,
            width=500,
            height=700,
            left=0,
            top=0,
            right=500,
            bottom=700,
        ).transform(
            source=self.pdf_source,
        )

    def test_pdf_source_create_text_document_cropped(self):
        document = transformers.PDFSourceCreateTextDocument(
            first_page=1,
            last_page=1,
            crop={"left": 0.0, "top": 0.1, "right": 1.0, "bottom": 0.9},
        ).transform(self.pdf_header_and_footer)
        self.assertEqual(
            document.dict(),
            self.get_expected("pdf_source_create_text_document_cropped"),
        )


if __name__ == "__main__":
    unittest.main()
