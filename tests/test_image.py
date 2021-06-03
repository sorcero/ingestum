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


from ingestum import sources
from ingestum import transformers

from tests import utils


image_source = sources.Image(path="tests/data/test.jpg")
table_source = sources.Image(path="tests/data/table.png")


def test_image_source_create_reference_text_document():
    source = image_source
    document = transformers.ImageSourceCreateReferenceTextDocument().transform(
        source=source
    )

    assert document.dict() == utils.get_expected(
        "image_source_create_reference_text_document"
    )


def test_image_source_create_text_document():
    source = image_source
    document = transformers.ImageSourceCreateTextDocument().transform(source=source)

    assert document.dict() == utils.get_expected("image_source_create_text_document")


def test_image_source_create_tabular_document():
    source = table_source
    document = transformers.ImageSourceCreateTabularDocument().transform(source=source)
    assert document.dict() == utils.get_expected("image_source_create_tabular_document")
