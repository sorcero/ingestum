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

from ingestum import sources
from ingestum import transformers


class XLSTestCase(unittest.TestCase):

    xls_source = sources.XLS(path="tests/data/test.xlsx")

    def setUp(self):
        os.mkdir("tests/files")

    def tearDown(self):
        shutil.rmtree("tests/files")

    def get_expected(self, transformer):
        filepath = "tests/output/" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_xls_source_create_csv_collection_document(self):
        source = self.xls_source
        document = transformers.XLSSourceCreateCSVCollectionDocument().transform(
            source=source
        )

        self.assertEqual(
            document.dict(),
            self.get_expected("xls_source_create_csv_collection_document"),
        )

    def test_xls_source_create_csv_document(self):
        source = self.xls_source
        document = transformers.XLSSourceCreateCSVDocument(sheet="Sheet1").transform(
            source=source
        )

        self.assertEqual(
            document.dict(), self.get_expected("xls_source_create_csv_document")
        )

    def test_xls_source_create_image(self):
        source = self.xls_source
        source = transformers.XLSSourceCreateImage(
            directory="tests/files",
            output="thumbnail.png",
        ).transform(source=source)
        document = transformers.ImageSourceCreateTextDocument().transform(source)
        self.assertEqual(document.dict(), self.get_expected("xls_source_create_image"))


if __name__ == "__main__":
    unittest.main()
