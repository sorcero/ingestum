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

import pytest

from ingestum import sources
from ingestum import transformers
from tests import utils


@pytest.mark.skipif(
    utils.skip_proquest, reason="INGESTUM_PROQUEST_* variables not found"
)
def test_proquest_source_create_xml_collection_document():
    source = sources.ProQuest()
    document = (
        transformers.ProQuestSourceCreateXMLCollectionDocument(
            query="Cardiothyrosis. Presentation of a clinical case",
            databases=["medlineprof"],
            articles=1,
        )
        .transform(source=source)
        .dict()
    )

    del document["context"]["proquest_source_create_xml_collection_document"][
        "timestamp"
    ]

    assert document["content"][0]["content"] != ""
    del document["content"][0]["content"]

    # We can't compare the 'origin' because it changes for each request
    assert document["content"][0]["origin"] != ""
    del document["content"][0]["origin"]

    assert document == utils.get_expected(
        "proquest_source_create_xml_collection_document"
    )


@pytest.mark.skipif(
    utils.skip_proquest, reason="INGESTUM_PROQUEST_* variables not found"
)
def test_proquest_source_create_publication_collection_document():
    source = sources.ProQuest()
    document = (
        transformers.ProQuestSourceCreatePublicationCollectionDocument(
            query="Cardiothyrosis. Presentation of a clinical case",
            databases=["medlineprof"],
            articles=1,
        )
        .transform(source=source)
        .dict()
    )

    del document["context"]["proquest_source_create_publication_collection_document"][
        "timestamp"
    ]

    assert document["content"][0]["abstract"] != ""
    del document["content"][0]["abstract"]

    # We can't compare the 'origin' because it changes for each request
    assert document["content"][0]["origin"] != ""
    del document["content"][0]["origin"]

    assert document == utils.get_expected(
        "proquest_source_create_publication_collection_document"
    )
