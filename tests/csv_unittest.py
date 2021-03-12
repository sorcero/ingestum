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
from ingestum import sources
from ingestum import transformers


class CSVTestCase(unittest.TestCase):
    def get_expected(self, transformer):
        filepath = "tests/output/" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_csv_document_create_tabular(self):
        csv_document = documents.CSV.parse_file("tests/input/csv_document.json")
        document = transformers.CSVDocumentCreateTabular().transform(
            document=csv_document
        )
        self.assertEqual(
            document.dict(), self.get_expected("csv_document_create_tabular")
        )

    def test_csv_source_create_document(self):
        csv_source = sources.CSV(path="tests/data/test.csv")
        document = transformers.CSVSourceCreateDocument().transform(source=csv_source)
        self.assertEqual(
            document.dict(), self.get_expected("csv_source_create_document")
        )


if __name__ == "__main__":
    unittest.main()
