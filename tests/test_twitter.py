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
from ingestum import documents
from ingestum import transformers
from tests import utils


source = sources.Twitter()


@pytest.mark.skipif(utils.skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_twitter_source_create_form_collection_document():
    transformer = transformers.TwitterSourceCreateFormCollectionDocument(
        search="twitter", count=10, sort="recent"
    )
    collection = transformer.transform(source=source)
    assert len(collection.content) > 0
    assert isinstance(collection.content[0], documents.Form)


@pytest.mark.skipif(utils.skip_twitter, reason="INGESTUM_TWITTER_* variables not found")
def test_twitter_source_create_publication_collection_document():
    transformer = transformers.TwitterSourceCreatePublicationCollectionDocument(
        search="twitter", count=10, sort="recent"
    )
    collection = transformer.transform(source=source)
    assert len(collection.content) > 0
    assert isinstance(collection.content[0], documents.Publication)
