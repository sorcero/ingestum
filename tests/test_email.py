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


@pytest.mark.skipif(utils.skip_email, reason="INGESTUM_EMAIL_* variables not found")
def test_email_source_create_html_collection_document():
    source = sources.Email()
    transformer = transformers.EmailSourceCreateHTMLCollectionDocument(hours=24)
    collection = transformer.transform(source=source)

    assert len(collection.content) > 0
    assert isinstance(collection.content[0], documents.HTML)


@pytest.mark.skipif(utils.skip_email, reason="INGESTUM_EMAIL_* variables not found")
def test_email_source_create_text_collection_document():
    source = sources.Email()
    transformer = transformers.EmailSourceCreateTextCollectionDocument(hours=24)
    collection = transformer.transform(source=source)

    assert len(collection.content) > 0
    assert isinstance(collection.content[0], documents.Text)
