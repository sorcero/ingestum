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

from ingestum import documents
from ingestum import transformers
from ingestum import conditionals


class PassageTestCase(unittest.TestCase):

    passage_document = documents.Passage.parse_file("tests/input/passage_document.json")

    def get_expected(self, transformer):
        filepath = "tests/output/" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_passage_document_add_metadata_from_metadata(self):
        transformer = transformers.PassageDocumentAddMetadataFromMetadata(
            source="tags", target="anchors"
        )
        document = transformer.transform(document=self.passage_document)

        self.assertEqual(
            document.dict(),
            self.get_expected("passage_document_add_metadata_from_metadata"),
        )

    def test_passage_document_add_metadata(self):
        document = transformers.PassageDocumentAddMetadata(
            key="tags", value="passage"
        ).transform(document=self.passage_document)

        self.assertEqual(
            document.dict(), self.get_expected("passage_document_add_metadata")
        )

    def test_passage_document_add_metadata_on_attribute(self):
        document = transformers.PassageDocumentAddMetadataOnAttribute(
            attribute="content", regexp="Lorem", key="tags", value="S%s"
        ).transform(document=self.passage_document)

        self.assertEqual(
            document.dict(),
            self.get_expected("passage_document_add_metadata_on_attribute"),
        )

    def test_passage_document_string_split(self):
        document = transformers.PassageDocumentStringSplit(regex="ipsum").transform(
            document=self.passage_document
        )

        self.assertEqual(
            document.dict(), self.get_expected("passage_document_string_split")
        )

    def test_passage_document_transform_on_conditional(self):
        document = transformers.PassageDocumentTransformOnConditional(
            conditional=conditionals.AllAttributeMatchesRegexp(
                attribute="title", expression="Sorcero"
            ),
            transformer=transformers.TextDocumentStringReplace(
                regexp="Lorem", replacement="Test Replacement"
            ),
        ).transform(document=self.passage_document)

        self.assertEqual(
            document.dict(),
            self.get_expected("passage_document_transform_on_conditional"),
        )


if __name__ == "__main__":
    unittest.main()
