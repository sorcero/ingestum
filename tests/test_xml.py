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


from ingestum import documents
from ingestum import sources
from ingestum import transformers
from ingestum.utils import write_document_to_path

from tests import utils


xml_source = sources.XML(path="tests/data/test.xml")
xml_document = documents.XML.parse_file("tests/input/xml_document.json")


def test_xml_create_text_document():
    document = transformers.XMLCreateTextDocument().transform(document=xml_document)
    assert document.dict() == utils.get_expected("xml_create_text_document")


def test_xml_document_tag_add_end_marker():
    document = transformers.XMLDocumentTagReplace(
        tag="food", replacement="{@tag}\n\n"
    ).transform(document=xml_document)
    assert document.dict() == utils.get_expected("xml_document_tag_add_end_marker")


def test_xml_document_tag_add_start_marker():
    document = transformers.XMLDocumentTagReplace(
        tag="food", replacement="FOOD{@tag}"
    ).transform(document=xml_document)
    assert document.dict() == utils.get_expected("xml_document_tag_add_start_marker")


def test_xml_document_tag_replace():
    document = transformers.XMLDocumentTagReplace(
        tag="food", replacement="replacement"
    ).transform(document=xml_document)
    write_document_to_path(document, "tests/output/xml_document_tag_replace.json")
    assert document.dict() == utils.get_expected("xml_document_tag_replace")


def test_xml_source_create_document():
    document = transformers.XMLSourceCreateDocument().transform(source=xml_source)
    assert document.dict() == utils.get_expected("xml_source_create_document")
