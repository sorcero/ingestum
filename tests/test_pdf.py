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
import shutil

from ingestum import documents
from ingestum import sources
from ingestum import transformers

from tests import utils


pdf_form = sources.PDF(path="tests/data/form.pdf")
pdf_source = sources.PDF(path="tests/data/test.pdf")
pdf_table_source = sources.PDF(path="tests/data/table.pdf")
pdf_header_and_footer = sources.PDF(path="tests/data/header_and_footer.pdf")
pdf_hybrid = sources.PDF(path="tests/data/hybrid.pdf")
pdf_tabular_collection_document = documents.Collection.parse_file(
    "tests/input/pdf_tabular_collection_document.json"
)
pdf_tabular_collection_document_md = documents.Collection.parse_file(
    "tests/input/pdf_tabular_collection_document_md.json"
)
pdf_publication = sources.PDF(path="tests/data/test_pdf_publication.pdf")
pdf_tabular_collection_document_hybrid = documents.Collection.parse_file(
    "tests/input/pdf_tabular_collection_document_hybrid.json"
)
pdf_tabular_collection_document_hybrid_md = documents.Collection.parse_file(
    "tests/input/pdf_tabular_collection_document_hybrid_md.json"
)


def setup_module():
    os.mkdir("/tmp/ingestum")


def teardown_module():
    shutil.rmtree("/tmp/ingestum")


def test_pdf_source_create_form_document():
    document = transformers.PDFSourceCreateFormDocument().transform(source=pdf_form)
    assert document.dict() == utils.get_expected("pdf_source_create_form_document")


def test_pdf_source_create_text_document():
    document = transformers.PDFSourceCreateTextDocument(
        first_page=1, last_page=3
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected("pdf_source_create_text_document")


def test_pdf_source_create_text_document_no_pages():
    document = transformers.PDFSourceCreateTextDocument().transform(source=pdf_source)
    assert document.dict() == utils.get_expected("pdf_source_create_text_document")


def test_pdf_source_create_text_document_ocr():
    document = transformers.PDFSourceCreateTextDocumentOCR(
        first_page=1, last_page=3
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected("pdf_source_create_text_document_ocr")


def test_pdf_source_create_text_document_ocr_no_pages():
    document = transformers.PDFSourceCreateTextDocumentOCR().transform(
        source=pdf_source
    )
    assert document.dict() == utils.get_expected("pdf_source_create_text_document_ocr")


def test_pdf_source_create_text_document_hybrid():
    document = transformers.PDFSourceCreateTextDocumentHybrid(
        first_page=1, last_page=1, layout="multi"
    ).transform(source=pdf_hybrid)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_hybrid"
    )


def test_pdf_source_create_text_document_hybrid_no_pages():
    document = transformers.PDFSourceCreateTextDocumentHybrid(layout="multi").transform(
        source=pdf_hybrid
    )
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_hybrid"
    )


def test_pdf_source_create_tabular_collection_document():
    document = transformers.PDFSourceCreateTabularCollectionDocument(
        first_page=1, last_page=3, options={"line_scale": 50}
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_tabular_collection_document"
    )


def test_pdf_source_create_tabular_collection_document_no_pages():
    document = transformers.PDFSourceCreateTabularCollectionDocument(
        options={"line_scale": 50}
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_tabular_collection_document"
    )


def test_pdf_source_create_tabular_collection_document_with_regexp():
    document = transformers.PDFSourceCreateTabularCollectionDocumentWithRegexp(
        first_page=1,
        last_page=1,
        start_regexp="^TABLE",
        end_regexp="Here",
    ).transform(source=pdf_table_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_tabular_collection_document_with_regexp"
    )


def test_pdf_source_create_tabular_collection_document_with_dividers():
    document = transformers.PDFSourceCreateTabularCollectionDocumentWithDividers(
        first_page=1,
        last_page=1,
        start_regexp="^TABLE",
        num_lines=3,
    ).transform(source=pdf_table_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_tabular_collection_document_with_dividers"
    )


def test_pdf_source_create_tabular_collection_document_hybrid():
    document = transformers.PDFSourceCreateTabularCollectionDocumentHybrid(
        first_page=1,
        last_page=1,
    ).transform(source=pdf_hybrid)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_tabular_collection_document_hybrid"
    )


def test_pdf_source_images_create_resource_collection_document():
    document = transformers.PDFSourceImagesCreateResourceCollectionDocument(
        directory="/tmp/ingestum", first_page=1, last_page=3
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_images_create_resource_collection_document"
    )


def test_pdf_source_images_create_resource_collection_document_no_pages():
    document = transformers.PDFSourceImagesCreateResourceCollectionDocument(
        directory="/tmp/ingestum", first_page=1, last_page=3
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_images_create_resource_collection_document"
    )


def test_pdf_source_shapes_create_resource_collection_document_no_pages():
    document = transformers.PDFSourceShapesCreateResourceCollectionDocument(
        directory="/tmp/ingestum"
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_shapes_create_resource_collection_document"
    )


def test_pdf_source_text_create_text_collection_document():
    document = transformers.PDFSourceTextCreateTextCollectionDocument(
        first_page=1,
        last_page=3,
        options={"line_margin": 0.60},
        regexp=r"Lorem((.)*)amet",
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_text_create_text_collection_document"
    )


def test_pdf_source_text_create_text_collection_document_no_pages():
    document = transformers.PDFSourceTextCreateTextCollectionDocument(
        options={"line_margin": 0.60},
        regexp=r"Lorem((.)*)amet",
    ).transform(source=pdf_source)
    assert document.dict() == utils.get_expected(
        "pdf_source_text_create_text_collection_document"
    )


def test_pdf_source_create_text_document_replaced_extractables():
    document = transformers.PDFSourceCreateTextDocumentReplacedExtractables(
        first_page=1, last_page=3
    ).transform(
        source=pdf_source,
        collection=pdf_tabular_collection_document,
        replacements=pdf_tabular_collection_document_md,
    )
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_replaced_extractables"
    )


def test_pdf_source_create_text_document_replaced_extractables_no_pages():
    document = transformers.PDFSourceCreateTextDocumentReplacedExtractables().transform(
        source=pdf_source,
        collection=pdf_tabular_collection_document,
        replacements=pdf_tabular_collection_document_md,
    )
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_replaced_extractables"
    )


def test_pdf_source_create_text_document_hybrid_replaced_extractables():
    document = transformers.PDFSourceCreateTextDocumentHybridReplacedExtractables(
        first_page=1, last_page=1, layout="multi"
    ).transform(
        source=pdf_hybrid,
        collection=pdf_tabular_collection_document_hybrid,
        replacements=pdf_tabular_collection_document_hybrid_md,
    )
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_hybrid_replaced_extractables"
    )


def test_pdf_source_create_text_document_hybrid_replaced_extractables_no_pages():
    document = transformers.PDFSourceCreateTextDocumentHybridReplacedExtractables(
        layout="multi"
    ).transform(
        source=pdf_hybrid,
        collection=pdf_tabular_collection_document_hybrid,
        replacements=pdf_tabular_collection_document_hybrid_md,
    )
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_hybrid_replaced_extractables"
    )


def test_pdf_source_crop_create_image_source():
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
        source=pdf_source,
    )


def test_pdf_source_create_text_document_cropped():
    document = transformers.PDFSourceCreateTextDocument(
        first_page=1,
        last_page=1,
        crop={"left": 0.0, "top": 0.1, "right": 1.0, "bottom": 0.9},
    ).transform(pdf_header_and_footer)
    assert document.dict() == utils.get_expected(
        "pdf_source_create_text_document_cropped"
    )


def test_pdf_to_publication():
    document = (
        transformers.PDFSourceCreatePublicationDocument()
        .transform(pdf_publication)
        .dict()
    )
    del document["abstract"]
    assert document == utils.get_expected("pdf_source_create_publication_document")
