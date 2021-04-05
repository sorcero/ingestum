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


import json
import unittest
import os
import shutil

from ingestum import documents
from ingestum import transformers
from ingestum import conditionals


class ConditionalsTestCase(unittest.TestCase):

    document = documents.Text.parse_file(path="tests/input/text_document.json")
    collection = documents.Collection.parse_file(
        path="tests/input/collection_has_document_with_conditional.json",
    )

    def setUp(self):
        os.mkdir("/tmp/ingestum")

    def tearDown(self):
        shutil.rmtree("/tmp/ingestum")

    def get_expected(self, transformer):
        filepath = "tests/output/conditionals_" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_collection_has_document_with_conditional(self):
        document = transformers.CollectionDocumentRemoveOnConditional(
            conditional=conditionals.CollectionHasDocumentWithConditional(
                conditional=conditionals.PassageHasContentPrefix(prefix="2")
            )
        ).transform(self.collection)
        self.assertEqual(
            document.dict(),
            self.get_expected("collection_has_document_with_conditional"),
        )

    def test_all_and_recursive(self):
        document = transformers.TextCreatePassageDocument().transform(self.document)
        document = transformers.PassageDocumentTransformOnConditional(
            conditional=conditionals.AllAnd(
                left_conditional=conditionals.AllAnd(
                    left_conditional=conditionals.PassageHasContentPrefix(
                        prefix="Lorem"
                    ),
                    right_conditional=conditionals.PassageHasContentPrefix(
                        prefix="Lorem"
                    ),
                ),
                right_conditional=conditionals.PassageHasContentPrefix(prefix="Lorem"),
            ),
            transformer=transformers.TextDocumentStringReplace(
                regexp="(l|L)orem", replacement="__REPLACED__"
            ),
        ).transform(document)
        self.assertEqual(
            document.dict(),
            self.get_expected("all_and_recursive"),
        )


if __name__ == "__main__":
    unittest.main()
