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


from ingestum import documents
from ingestum import transformers
from ingestum import conditionals

from tests import utils


collection_document1 = documents.Collection.parse_file(
    "tests/input/collection_document1.json"
)
collection_document2 = documents.Collection.parse_file(
    "tests/input/collection_document2.json"
)
collection_passage_document = documents.Collection.parse_file(
    "tests/input/collection_passage_document.json"
)
collection_collection_document = documents.Collection.parse_file(
    "tests/input/collection_collection_document.json"
)
tabular_document = documents.Tabular.parse_file("tests/input/tabular_document.json")


def test_collection_document_add():
    document = transformers.CollectionDocumentAdd().transform(
        collection=collection_document1, document=tabular_document
    )
    assert document.dict() == utils.get_expected("collection_document_add")


def test_collection_document_join():
    document = transformers.CollectionDocumentJoin(
        transformer=transformers.TabularDocumentJoin()
    ).transform(collection=collection_document1)
    assert document.dict() == utils.get_expected("collection_document_join")


def test_collection_document_merge():
    document = transformers.CollectionDocumentMerge().transform(
        collection_1=collection_document1,
        collection_2=collection_document2,
    )
    assert document.dict() == utils.get_expected("collection_document_merge")


def test_collection_document_remove_on_conditional():
    document = transformers.CollectionDocumentRemoveOnConditional(
        conditional=conditionals.AllAttributeMatchesRegexp(
            attribute="content", expression="Lorem"
        )
    ).transform(collection=collection_passage_document)
    assert document.dict() == utils.get_expected(
        "collection_document_remove_on_conditional"
    )


def test_collection_document_transform():
    document = transformers.CollectionDocumentTransform(
        transformer=transformers.TabularDocumentCreateMDPassage()
    ).transform(collection=collection_document1)
    assert document.dict() == utils.get_expected("collection_document_transform")


def test_collection_document_transform_recursive():
    document = transformers.CollectionDocumentTransform(
        transformer=transformers.CollectionDocumentTransform(
            transformer=transformers.TextDocumentStringReplace(
                regexp="TEXT", replacement="REPLACED"
            )
        ),
    ).transform(collection_collection_document)
    assert document.dict() == utils.get_expected(
        "collection_document_transform_recursive"
    )


def test_collection_document_transform_on_conditional():
    document = transformers.CollectionDocumentTransformOnConditional(
        conditional=conditionals.AllAttributeMatchesRegexp(
            attribute="content", expression="Lorem"
        ),
        transformer=transformers.TextDocumentStringReplace(
            regexp="Lorem", replacement="Test Replacement"
        ),
    ).transform(collection=collection_passage_document)
    assert document.dict() == utils.get_expected(
        "collection_document_transform_on_conditional"
    )
