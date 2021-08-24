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
import shutil

from ingestum import sources
from ingestum import transformers

from tests import utils


xls_source = sources.XLS(path="tests/data/test.xlsx")
xls_source_test_stringify = sources.XLS(path="tests/data/test_stringify.xlsx")


def setup_module():
    os.mkdir("/tmp/ingestum")


def teardown_module():
    shutil.rmtree("/tmp/ingestum")


def test_xls_source_create_tabular_collection_document():
    source = xls_source
    document = transformers.XLSSourceCreateTabularCollectionDocument().transform(
        source=source
    )

    assert document.dict() == utils.get_expected(
        "xls_source_create_tabular_collection_document"
    )


def test_xls_source_create_tabular_document():
    source = xls_source
    document = transformers.XLSSourceCreateTabularDocument(sheet="Sheet1").transform(
        source=source
    )

    assert document.dict() == utils.get_expected("xls_source_create_tabular_document")


def test_xls_source_create_image():
    source = xls_source
    source = transformers.XLSSourceCreateImage(
        directory="/tmp/ingestum",
        output="thumbnail.png",
    ).transform(source=source)
    document = transformers.ImageSourceCreateTextDocument().transform(source)
    assert document.dict() == utils.get_expected("xls_source_create_image")


def test_xls_source_create_tabular_document_stringify():
    source = xls_source_test_stringify
    document = transformers.XLSSourceCreateTabularDocument(sheet="Sheet1").transform(
        source=source
    )
    assert document.dict() == utils.get_expected(
        "xls_source_create_tabular_document_stringify"
    )
