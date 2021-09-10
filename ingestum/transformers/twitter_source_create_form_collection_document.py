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
import logging
import tweepy

from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

# Since there are limits to GET calls to Twitter API, we need to make
# sure we do not exceed them.
# https://developer.twitter.com/en/docs/basics/rate-limits
# QUERY_CALLS_LIMIT = 450
QUERY_CALLS_LIMIT = 1


class Transformer(BaseTransformer):
    """
    Transforms a `Twitter` source into a `Collection` of `Form` documents with
    the result of the search.

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

    class ArgumentsModel(BaseModel):
        search: str
        tags: Optional[List[str]] = []
        count: Optional[int] = 100
        sort: Optional[str] = "recent"

    class InputsModel(BaseModel):
        source: sources.Twitter

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def search_twitter(self, source):
        python_api = source.get_api()
        return [
            status
            for status in tweepy.Cursor(
                python_api.search,
                q=self.arguments.search,
                tweet_mode="extended",
                result_type=self.arguments.sort,
                wait_on_rate_limit=True,
                wait_on_rate_limit_notify=True,
            ).items(self.arguments.count)
        ]

    def get_document(self, source, status, tags):
        status_json = status._json

        tweet = {}
        tweet["content"] = {}
        for tag in tags:
            if tag == "full_text":
                # RT'd tweets are truncated, so we must access the
                # original tweet to get the full text
                try:
                    tweet["content"]["full_text"] = status.retweeted_status.full_text
                except:
                    tweet["content"]["full_text"] = status.full_text
            else:
                tweet["content"][tag] = status_json[tag]
        tweet[
            "origin"
        ] = f"https://twitter.com/{status_json['user']['screen_name']}/status/{status_json['id']}"

        return documents.Form.new_from(source, **tweet)

    def transform(self, source: sources.Twitter) -> documents.Collection:
        super().transform(source=source)

        content = []
        tweets = self.search_twitter(source)

        tags = self.arguments.tags if self.arguments.tags != [] else ["full_text"]
        for tweet in tweets:
            document = self.get_document(source=source, status=tweet, tags=tags)
            content.append(document)

        title = "Twitter search for %s" % self.arguments.search

        return documents.Collection.new_from(None, title=title, content=content)
