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

from ingestum import documents
from ingestum import transformers


class ResourceTestCase(unittest.TestCase):

    resource_document = documents.Resource.parse_file(
        "tests/input/resource_document.json"
    )

    def setUp(self):
        os.mkdir("tests/files")

    def tearDown(self):
        shutil.rmtree("tests/files")

    def get_expected(self, transformer):
        filepath = "tests/output/" + transformer + ".json"
        with open(filepath, "r") as f:
            expected = json.loads(f.read())
        return expected

    def test_resource_create_text_document(self):
        document = transformers.ResourceCreateTextDocument().transform(
            document=self.resource_document
        )
        self.assertEqual(
            document.dict(), self.get_expected("resource_create_text_document")
        )


if __name__ == "__main__":
    unittest.main()
