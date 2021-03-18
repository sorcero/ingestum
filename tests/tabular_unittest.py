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


class TabularTestCase(unittest.TestCase):

    tabular_document1 = documents.Tabular.parse_file(
        "tests/input/tabular_document1.json"
    )
    tabular_document2 = documents.Tabular.parse_file(
        "tests/input/tabular_document2.json"
    )
    tabular_extractables = documents.Collection.parse_file(
        "tests/input/tabular_extractables.json"
    )
    tabular_collection = documents.Collection.parse_file(
        "tests/input/tabular_collection.json"
    )

    def get_expected(self, transformer):
        filepath = "tests/output/" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_tabular_document_cell_transpose_on_conditional(self):
        document = transformers.TabularDocumentCellTransposeOnConditional(
            conditional=conditionals.TabularRowMatchesRegexp(column=2, regexp="Rachel"),
            column=2,
            position=None,
            reverse=False,
        ).transform(document=self.tabular_document1)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_cell_transpose_on_conditional"),
        )

    def test_tabular_document_columns_insert(self):
        document = transformers.TabularDocumentColumnsInsert(
            position=3, columns=2
        ).transform(self.tabular_document1)
        self.assertEqual(
            document.dict(), self.get_expected("tabular_document_columns_insert")
        )

    def test_tabular_document_columns_string_replace(self):
        document = transformers.TabularDocumentColumnsStringReplace(
            column=2, expression="Craig", replacement="Charles"
        ).transform(self.tabular_document1)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_columns_string_replace"),
        )

    def test_tabular_document_columns_update_with_extractables(self):
        document = transformers.TabularDocumentColumnsUpdateWithExtractables(
            columns=[2], regexp=r"row1"
        ).transform(
            collection=self.tabular_collection, extractables=self.tabular_extractables
        )
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_columns_update_with_extractables"),
        )

    def test_tabular_document_create_form_collection(self):
        document = transformers.TabularDocumentCreateFormCollection(
            format={0: "username", 1: "identifier", 2: "first_name", 3: "last_name"}
        ).transform(self.tabular_document2)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_create_form_collection"),
        )

    def test_tabular_document_create_form_collection_with_headers(self):
        document = transformers.TabularDocumentCreateFormCollectionWithHeaders(
            headers={0: "username", 1: "identifier", 2: "first_name", 3: "last_name"},
            clues=r"(Username)|(Identifier)|(First name)|(Last name)",
        ).transform(self.tabular_document1)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_create_form_collection_with_headers"),
        )

    def test_tabular_document_create_md_passage(self):
        document = transformers.TabularDocumentCreateMDPassage(
            format={0: "username", 1: "identifier", 2: "first_name", 3: "last_name"}
        ).transform(self.tabular_document1)
        self.assertEqual(
            document.dict(), self.get_expected("tabular_document_create_md_passage")
        )

    def test_tabular_document_fit(self):
        document = transformers.TabularDocumentFit(columns=2).transform(
            self.tabular_document1
        )
        self.assertEqual(document.dict(), self.get_expected("tabular_document_fit"))

    def test_tabular_document_join(self):
        document = transformers.TabularDocumentJoin().transform(
            document_1=self.tabular_document1, document_2=self.tabular_document2
        )
        self.assertEqual(document.dict(), self.get_expected("tabular_document_join"))

    def test_tabular_document_row_merge_on_conditional(self):
        document = transformers.TabularDocumentRowMergeOnConditional(
            conditional=conditionals.TabularRowMatchesRegexp(column=1, regexp="4081")
        ).transform(document=self.tabular_document1)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_row_merge_on_conditional"),
        )

    def test_tabular_document_row_remove_on_conditional(self):
        document = transformers.TabularDocumentRowRemoveOnConditional(
            conditional=conditionals.TabularRowMatchesRegexp(column=1, regexp="4081")
        ).transform(document=self.tabular_document1)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_row_remove_on_conditional"),
        )

    def test_tabular_document_strip_until_conditional(self):
        document = transformers.TabularDocumentStripUntilConditional(
            conditional=conditionals.TabularRowMatchesRegexp(column=1, regexp="4081")
        ).transform(document=self.tabular_document1)
        self.assertEqual(
            document.dict(),
            self.get_expected("tabular_document_strip_until_conditional"),
        )


if __name__ == "__main__":
    unittest.main()
