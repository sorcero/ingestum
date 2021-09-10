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
from ..utils import date_to_default_format

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
    :param count: The number of results to try and retrieve (defaults to 100)
    :type count: Optional[int]
    :param sort: Type of search results you would prefer to receive
        The options are: ``"recent"``, ``"popular"``, ``"mixed"``; defaults to ``"recent"``
    :type sort: Optional[str]
    """

    type: Literal[__script__] = __script__

    def get_publication_date(self, created_at):
        return date_to_default_format(created_at)

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

    def get_content(self, status):
        try:
            return status.retweeted_status.full_text
        except:
            return status.full_text

    def get_document(self, source, status, tags):
        status_json = status._json
        tweet = {}

        tweet["authors"] = [self.get_author(status_json["user"]["screen_name"])]
        tweet["content"] = self.get_content(status)
        tweet["country"] = self.get_country(status_json["place"])
        tweet["language"] = status_json["metadata"]["iso_language_code"]
        tweet["keywords"] = self.get_keywords(status_json["entities"]["hashtags"])
        tweet[
            "origin"
        ] = f"https://twitter.com/{status_json['user']['screen_name']}/status/{status_json['id']}"
        tweet["provider"] = "twitter"
        tweet["provider_id"] = status_json["id_str"]
        tweet["publication_date"] = self.get_publication_date(status.created_at)  ######
        tweet["publication_type"] = self.get_publication_type(status_json)

        tweet["context"] = {}
        tweet["context"][self.type] = {}

        # User information
        tweet["context"][self.type]["user"] = {}
        tweet["context"][self.type]["user"]["followers_count"] = status_json["user"][
            "followers_count"
        ]
        tweet["context"][self.type]["user"]["screen_name"] = status_json["user"][
            "screen_name"
        ]
        tweet["context"][self.type]["user"]["url"] = status_json["user"]["url"]
        tweet["context"][self.type]["user"]["verified"] = status_json["user"][
            "verified"
        ]

        # Reach information
        tweet["context"][self.type]["retweet_count"] = status_json["retweet_count"]
        tweet["context"][self.type]["favorite_count"] = status_json["favorite_count"]

        return documents.Publication.new_from(source, **tweet)

    def transform(self, source: sources.Twitter) -> documents.Collection:
        return super().transform(source=source)
