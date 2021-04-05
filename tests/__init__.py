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

import os
import logging

from tests.audio_unittest import AudioTestCase
from tests.collection_unittest import CollectionTestCase
from tests.csv_unittest import CSVTestCase
from tests.html_unittest import HTMLTestCase
from tests.image_unittest import ImageTestCase
from tests.passage_unittest import PassageTestCase
from tests.pdf_unittest import PDFTestCase
from tests.pipelines_unittest import PipelinesTestCase
from tests.resource_unittest import ResourceTestCase
from tests.scripts_unittest import ScriptsTestCase
from tests.tabular_unittest import TabularTestCase
from tests.text_unittest import TextTestCase
from tests.twitter_unittest import TwitterTestCase
from tests.xls_unittest import XLSTestCase
from tests.xml_unittest import XMLTestCase
from tests.docx_unittest import DOCXTestCase
from tests.conditionals_unittest import ConditionalsTestCase

assert AudioTestCase
assert CollectionTestCase
assert CSVTestCase
assert HTMLTestCase
assert ImageTestCase
assert PassageTestCase
assert PDFTestCase
assert PipelinesTestCase
assert ResourceTestCase
assert ScriptsTestCase
assert TabularTestCase
assert TextTestCase
assert TwitterTestCase
assert XLSTestCase
assert XMLTestCase
assert DOCXTestCase
assert ConditionalsTestCase

if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s:%(message)s",
        level=os.getenv("LOGGER_LEVEL", logging.WARNING),
    )
    unittest.main()
