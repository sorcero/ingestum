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
import logging

from typing_extensions import Literal

from .. import documents
from .. import sources
from .twitter_source_create_form_collection_document import (
    Transformer as BaseTwitterTransformer,
)

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

# Since there are limits to GET calls to Twitter API, we need to make
# sure we do not exceed them.
# https://developer.twitter.com/en/docs/basics/rate-limits
# QUERY_CALLS_LIMIT = 450
QUERY_CALLS_LIMIT = 1


class Transformer(BaseTwitterTransformer):
    """
    Transforms a `Twitter` source into a `Collection` of `Publication`
    documents with the result of the search.

    :param search: The search string to pass to a twitter query, e.g., Epiduo
        https://twitter.com/search?q=Epiduo
    :type search: str
    :param tags: The list of tags to pull from each tweet
    :type tags: Optional[List[str]]
    """

    type: Literal[__script__] = __script__

    def get_publication_date(self, created_at):
        split = created_at.split(" ")
        return f"{split[-1]}-{split[1]}-{split[2]}"

    def get_publication_type(self, tweet):
        publication_type = ["tweet"]
        if "retweeted_status" in tweet:
            publication_type.append("retweet")
        if tweet["is_quote_status"] is True:
            publication_type.append("quote")
        return publication_type

    def get_author(self, name):
        return documents.publication.Author(name=name, affiliation=[])

    def get_country(self, place):
        if place is not None and "country_code" in place:
            return place["country_code"]
        return ""

    def get_keywords(self, hashtags):
        keywords = []
        for hashtag in hashtags:
            keywords.append(hashtag["text"])
        return keywords

    def get_document(self, source, status, tags):
        tweet = {}

        tweet["authors"] = [self.get_author(status["user"]["screen_name"])]
        tweet["content"] = status["text"]
        tweet["country"] = self.get_country(status["place"])
        tweet["language"] = status["metadata"]["iso_language_code"]
        tweet["keywords"] = self.get_keywords(status["entities"]["hashtags"])
        tweet[
            "origin"
        ] = f"https://twitter.com/{status['user']['screen_name']}/status/{status['id']}"
        tweet["provider"] = "twitter"
        tweet["provider_id"] = status["id_str"]
        tweet["publication_date"] = self.get_publication_date(status["created_at"])
        tweet["publication_type"] = self.get_publication_type(status)

        tweet["context"] = {}
        tweet["context"][self.type] = {}

        # User information
        tweet["context"][self.type]["user"] = {}
        tweet["context"][self.type]["user"]["followers_count"] = status["user"][
            "followers_count"
        ]
        tweet["context"][self.type]["user"]["screen_name"] = status["user"][
            "screen_name"
        ]
        tweet["context"][self.type]["user"]["url"] = status["user"]["url"]
        tweet["context"][self.type]["user"]["verified"] = status["user"]["verified"]

        # Reach information
        tweet["context"][self.type]["retweet_count"] = status["retweet_count"]
        tweet["context"][self.type]["favorite_count"] = status["favorite_count"]

        return documents.Publication.new_from(source, **tweet)

    def transform(self, source: sources.Twitter) -> documents.Collection:
        return super().transform(source=source)
