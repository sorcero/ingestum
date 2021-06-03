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

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


html_source = sources.HTML(path=os.path.join(ROOT_DIR, "tests/data/test.html"))
html_document = documents.HTML.parse_file(path="tests/input/html_document.json")
html_image_document = documents.HTML.parse_file(
    path="tests/input/html_image_document.json"
)
html_sub_sup_document = documents.HTML.parse_file(
    path="tests/input/html_sub_sup_document.json"
)


def setup_module():
    os.mkdir("/tmp/ingestum")


def teardown_module():
    shutil.rmtree("/tmp/ingestum")


def test_html_document_images_extract():
    document = transformers.HTMLDocumentImagesExtract(
        directory="/tmp/ingestum"
    ).transform(document=html_image_document)
    assert document.dict() == utils.get_expected("html_document_images_extract")


def test_html_document_sub_replace_for_unicode():
    document = transformers.HTMLDocumentSubReplaceForUnicode().transform(
        document=html_sub_sup_document
    )
    assert document.dict() == utils.get_expected(
        "html_document_sub_replace_for_unicode"
    )


def test_html_document_sup_replace_for_unicode():
    document = transformers.HTMLDocumentSupReplaceForUnicode().transform(
        document=html_sub_sup_document
    )
    assert document.dict() == utils.get_expected(
        "html_document_sup_replace_for_unicode"
    )


def test_html_source_create_document():
    document = transformers.HTMLSourceCreateDocument().transform(source=html_source)
    assert document.dict() == utils.get_expected("html_source_create_document")


def test_html_source_create_image_source():
    source = transformers.HTMLSourceCreateImageSource(
        url=None,
        directory="/tmp/ingestum",
    ).transform(source=html_source)

    document = transformers.ImageSourceCreateTextDocument().transform(source=source)

    assert document.dict() == utils.get_expected("html_source_create_image_source")
