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
import unittest

from ingestum import sources
from ingestum import documents
from ingestum import transformers

skip_twitter = (
    os.environ.get("INGESTUM_TWITTER_CONSUMER_KEY") is None
    or os.environ.get("INGESTUM_TWITTER_CONSUMER_SECRET") is None
    or os.environ.get("INGESTUM_TWITTER_ACCESS_TOKEN") is None
    or os.environ.get("INGESTUM_TWITTER_ACCESS_SECRET") is None
)


class TwitterTestCase(unittest.TestCase):
    source = sources.Twitter()

    @unittest.skipIf(skip_twitter, "INGESTUM_TWITTER_* variables not found")
    def test_twitter_source_create_form_collection_document(self):
        transformer = transformers.TwitterSourceCreateFormCollectionDocument(
            search="twitter"
        )
        collection = transformer.transform(source=self.source)
        self.assertTrue(len(collection.content) > 0)
        self.assertTrue(isinstance(collection.content[0], documents.Form))


if __name__ == "__main__":
    unittest.main()
