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


import unittest

from ingestum import documents
from ingestum import sources
from ingestum import transformers

from tests import utils


class TextTestCase(unittest.TestCase):

    text_source = sources.Text(path="tests/data/test.txt")
    text_document = documents.Text.parse_file("tests/input/text_document.json")
    xml_text_document = documents.Text.parse_file("tests/input/text_to_xml.json")

    def test_text_create_passage_document(self):
        source = self.text_document
        document = transformers.TextCreatePassageDocument().transform(document=source)

        self.assertEqual(
            document.dict(), utils.get_expected("text_create_passage_document")
        )

    def test_text_create_xml_document(self):
        source = self.xml_text_document
        document = transformers.TextCreateXMLDocument().transform(document=source)

        self.assertEqual(document.dict(), utils.get_expected("text_to_xml"))

    def test_text_document_add_passage_marker(self):
        source = self.text_document
        document = transformers.TextDocumentAddPassageMarker(
            regexp="(\n)(\n)", marker="SEC"
        ).transform(document=source)

        self.assertEqual(
            document.dict(), utils.get_expected("text_document_add_passage_marker")
        )

    def test_text_document_hyphens_remove(self):
        source = self.text_document
        document = transformers.TextDocumentHyphensRemove().transform(document=source)

        self.assertEqual(
            document.dict(), utils.get_expected("text_document_hyphens_remove")
        )

    def test_text_document_string_replace(self):
        source = self.text_document
        document = transformers.TextDocumentStringReplace(
            regexp="ipsum", replacement="replacement"
        ).transform(document=source)

        self.assertEqual(
            document.dict(), utils.get_expected("text_document_string_replace")
        )

    def test_text_source_create_document(self):
        source = self.text_source
        document = transformers.TextSourceCreateDocument().transform(source=source)

        self.assertEqual(
            document.dict(), utils.get_expected("text_source_create_document")
        )

    def test_text_split_into_collection_document(self):
        source = self.text_document
        document = transformers.TextSplitIntoCollectionDocument(
            separator="\n\n"
        ).transform(document=source)

        self.assertEqual(
            document.dict(), utils.get_expected("text_split_into_collection_document")
        )


if __name__ == "__main__":
    unittest.main()
