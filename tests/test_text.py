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
import pytest

from ingestum import documents
from ingestum import sources
from ingestum import transformers

from tests import utils

skip_dictionary = os.environ.get("NLTK_DATA") is None

text_source = sources.Text(path="tests/data/test.txt")
text_document = documents.Text.parse_file("tests/input/text_document.json")
xml_text_document = documents.Text.parse_file("tests/input/text_to_xml.json")


def test_text_create_passage_document():
    source = text_document
    document = transformers.TextCreatePassageDocument().transform(document=source)

    assert document.dict() == utils.get_expected("text_create_passage_document")


def test_text_create_xml_document():
    source = xml_text_document
    document = transformers.TextCreateXMLDocument().transform(document=source)

    assert document.dict() == utils.get_expected("text_to_xml")


def test_text_document_add_passage_marker():
    source = text_document
    document = transformers.TextDocumentAddPassageMarker(
        regexp="(\n)(\n)", marker="SEC"
    ).transform(document=source)

    assert document.dict() == utils.get_expected("text_document_add_passage_marker")


@pytest.mark.skipif(skip_dictionary, reason="NLTK_DATA not found")
def test_text_document_hyphens_remove():
    source = text_document
    document = transformers.TextDocumentHyphensRemove().transform(document=source)

    assert document.dict() == utils.get_expected("text_document_hyphens_remove")


def test_text_document_string_replace():
    source = text_document
    document = transformers.TextDocumentStringReplace(
        regexp="ipsum", replacement="replacement"
    ).transform(document=source)

    assert document.dict() == utils.get_expected("text_document_string_replace")


def test_text_source_create_document():
    source = text_source
    document = transformers.TextSourceCreateDocument().transform(source=source)

    assert document.dict() == utils.get_expected("text_source_create_document")


def test_text_split_into_collection_document():
    source = text_document
    document = transformers.TextSplitIntoCollectionDocument(separator="\n\n").transform(
        document=source
    )

    assert document.dict() == utils.get_expected("text_split_into_collection_document")
