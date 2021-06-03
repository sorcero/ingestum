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


import os
import shutil

from ingestum import documents
from ingestum import transformers
from ingestum import conditionals

from tests import utils


document = documents.Text.parse_file(path="tests/input/text_document.json")
collection = documents.Collection.parse_file(
    path="tests/input/collection_has_document_with_conditional.json",
)


def setup_module():
    os.mkdir("/tmp/ingestum")


def teardown_module():
    shutil.rmtree("/tmp/ingestum")


def test_collection_has_document_with_conditional():
    document = transformers.CollectionDocumentRemoveOnConditional(
        conditional=conditionals.CollectionHasDocumentWithConditional(
            conditional=conditionals.PassageHasContentPrefix(prefix="2")
        )
    ).transform(collection)
    assert document.dict() == utils.get_expected(
        "conditionals_collection_has_document_with_conditional"
    )


def test_all_and_recursive():
    global document

    document = transformers.TextCreatePassageDocument().transform(document)
    document = transformers.PassageDocumentTransformOnConditional(
        conditional=conditionals.AllAnd(
            left_conditional=conditionals.AllAnd(
                left_conditional=conditionals.PassageHasContentPrefix(prefix="Lorem"),
                right_conditional=conditionals.PassageHasContentPrefix(prefix="Lorem"),
            ),
            right_conditional=conditionals.PassageHasContentPrefix(prefix="Lorem"),
        ),
        transformer=transformers.TextDocumentStringReplace(
            regexp="(l|L)orem", replacement="__REPLACED__"
        ),
    ).transform(document)
    assert document.dict() == utils.get_expected("conditionals_all_and_recursive")
