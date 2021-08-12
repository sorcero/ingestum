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

import pytest

from ingestum import sources
from ingestum import transformers
from tests import utils


@pytest.mark.skipif(utils.skip_biorxiv, reason="INGESTUM_BIORXIV_* variables not found")
def test_biorxiv_source_create_publication_collection_document():
    source = sources.Biorxiv()
    document = (
        transformers.BiorxivSourceCreatePublicationCollectionDocument(
            query="2021.07.28.453844", articles=1, hours=-1
        )
        .transform(source=source)
        .dict()
    )

    del document["content"][0]["abstract"]
    del document["context"]["biorxiv_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected(
        "biorxiv_source_create_publication_collection_document"
    )


@pytest.mark.skipif(utils.skip_medrxiv, reason="INGESTUM_MEDRXIV_* variables not found")
def test_biorxiv_source_create_publication_collection_document_with_medrxiv():
    source = sources.Biorxiv()
    document = (
        transformers.BiorxivSourceCreatePublicationCollectionDocument(
            query="2021.07.15.21260600", articles=1, hours=-1, repo="medrxiv"
        )
        .transform(source=source)
        .dict()
    )

    del document["content"][0]["abstract"]
    del document["context"]["biorxiv_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected(
        "biorxiv_source_create_publication_collection_document_with_medrxiv"
    )


@pytest.mark.skipif(utils.skip_medrxiv, reason="INGESTUM_MEDRXIV_* variables not found")
def test_biorxiv_source_create_publication_collection_document_with_filters():
    source = sources.Biorxiv()
    document = (
        transformers.BiorxivSourceCreatePublicationCollectionDocument(
            query="2021.07.15.21260600",
            articles=1,
            hours=-1,
            repo="medrxiv",
            filters={"jcode": "biorxiv"},
        )
        .transform(source=source)
        .dict()
    )

    del document["context"]["biorxiv_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document == utils.get_expected(
        "biorxiv_source_create_publication_collection_document_with_filters"
    )
